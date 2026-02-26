// Build: 2025/02/27 飞猪旅行去广告脚本 - 图片/视频过滤版
(() => {
    // 定义飞猪相关域名列表（包含合作伙伴）
    const FLIGGY_DOMAINS = [
        // 飞猪主域名
        'fliggy.com', 'feizhu.com', 'feizhu.cn', 'feizhu.net',
        'alitrip.com', 'v.bcvbw.com', 'ulk.alimama.com',
        // 关联域名
        'xiaozhu.com', 'm.amap.com', 'ulink.alipay.com',
        'ace.tb.cn', 'mobile.tmall.com', 'dp.ctrip.com',
        'weibo.cn', 'xiaohongshu.com',
        // 子域名通配
        '.fliggy.com', '.feizhu.com', '.alitrip.com',
        '.taobao.com', '.tmall.com', '.alibaba.com'
    ];

    // 检查当前请求是否属于飞猪相关域名
    function isFliggyRequest(url) {
        if (!url) return false;
        try {
            const urlObj = new URL(url);
            const hostname = urlObj.hostname.toLowerCase();
            return FLIGGY_DOMAINS.some(domain => 
                hostname === domain || hostname.endsWith('.' + domain)
            );
        } catch (e) {
            return false;
        }
    }

    // 获取客户端实例
    const client = (() => {
        if (typeof $task !== 'undefined') return 'quantumultx';
        if (typeof $httpClient !== 'undefined') return 'surge';
        if (typeof $loon !== 'undefined') return 'loon';
        return 'unknown';
    })();

    // 日志工具
    const logger = {
        debug: (msg) => {
            if (process.env.DEBUG === 'true') console.log(`[Fliggy AdBlock] ${msg}`);
        },
        info: (msg) => console.log(`[Fliggy AdBlock] ${msg}`)
    };

    // 检查是否为图片请求
    function isImageRequest(url, headers) {
        const urlLower = url.toLowerCase();
        const contentType = headers['Content-Type'] || headers['content-type'] || '';
        
        // 检查URL扩展名
        const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico'];
        if (imageExts.some(ext => urlLower.includes(ext))) return true;
        
        // 检查Content-Type
        if (contentType.startsWith('image/')) return true;
        
        return false;
    }

    // 检查是否为GIF（动图）
    function isGifImage(url, headers) {
        const urlLower = url.toLowerCase();
        const contentType = headers['Content-Type'] || headers['content-type'] || '';
        
        return urlLower.includes('.gif') || contentType === 'image/gif';
    }

    // 检查是否为视频请求
    function isVideoRequest(url, headers) {
        const urlLower = url.toLowerCase();
        const contentType = headers['Content-Type'] || headers['content-type'] || '';
        
        const videoExts = ['.mp4', '.m3u8', '.ts', '.mov', '.avi', '.mkv', '.flv', '.webm'];
        if (videoExts.some(ext => urlLower.includes(ext))) return true;
        if (contentType.startsWith('video/')) return true;
        
        return false;
    }

    // 尝试从响应头或URL获取资源大小/时长信息
    function getResourceInfo(response, url) {
        const info = {
            size: null,
            duration: null,
            dimensions: null
        };
        
        // 从Content-Length获取大小
        const contentLength = response.headers['Content-Length'] || response.headers['content-length'];
        if (contentLength) {
            info.size = parseInt(contentLength, 10);
        }
        
        // 视频时长通常需要解析内容，这里简单返回null
        // 实际场景可能需要分析MP4头信息或m3u8文件
        
        return info;
    }

    // 处理请求
    function handleRequest() {
        const request = typeof $request !== 'undefined' ? $request : null;
        const response = typeof $response !== 'undefined' ? $response : null;
        
        if (!request) {
            // 没有请求信息，无法处理
            $done({});
            return;
        }
        
        const url = request.url;
        
        // 如果不是飞猪相关域名，直接放行
        if (!isFliggyRequest(url)) {
            $done({});
            return;
        }
        
        logger.info(`Processing: ${url}`);
        
        // 如果有响应体（响应阶段）
        if (response) {
            const headers = response.headers || {};
            
            // 过滤规则1：所有动图（GIF）返回404
            if (isGifImage(url, headers)) {
                logger.info(`Blocked GIF: ${url}`);
                $done({
                    status: 404,
                    headers: {'Content-Type': 'text/plain'},
                    body: 'GIF images are blocked'
                });
                return;
            }
            
            // 过滤规则2：图片大小过滤（超过半屏的图片）
            if (isImageRequest(url, headers)) {
                const contentLength = headers['Content-Length'] || headers['content-length'];
                if (contentLength) {
                    const sizeInKB = parseInt(contentLength, 10) / 1024;
                    // 假设半屏图片约200KB（根据实际情况调整）
                    if (sizeInKB > 200) {
                        logger.info(`Blocked large image: ${url}, size: ${sizeInKB.toFixed(2)}KB`);
                        $done({
                            status: 404,
                            headers: {'Content-Type': 'text/plain'},
                            body: 'Large images are blocked'
                        });
                        return;
                    }
                }
            }
            
            // 过滤规则3：视频时长过滤（少于10秒的视频）
            if (isVideoRequest(url, headers)) {
                // 尝试从URL或响应头获取视频时长
                // 这里简化处理：对m3u8播放列表进行检查
                if (url.includes('.m3u8') && response.body) {
                    try {
                        const bodyStr = typeof response.body === 'string' ? 
                            response.body : 
                            new TextDecoder().decode(response.bodyBytes || new Uint8Array());
                        
                        // 解析m3u8文件，计算总时长
                        const lines = bodyStr.split('\n');
                        let totalDuration = 0;
                        let segmentCount = 0;
                        
                        for (const line of lines) {
                            if (line.startsWith('#EXTINF:')) {
                                const duration = parseFloat(line.split(':')[1].split(',')[0]);
                                totalDuration += duration;
                                segmentCount++;
                            }
                        }
                        
                        // 如果有分段信息
                        if (segmentCount > 0) {
                            logger.info(`Video duration: ${totalDuration}s, segments: ${segmentCount}`);
                            
                            // 少于10秒的视频返回404
                            if (totalDuration < 10) {
                                logger.info(`Blocked short video: ${url}, duration: ${totalDuration}s`);
                                $done({
                                    status: 404,
                                    headers: {'Content-Type': 'text/plain'},
                                    body: 'Videos shorter than 10 seconds are blocked'
                                });
                                return;
                            }
                        }
                    } catch (e) {
                        logger.debug(`Error parsing m3u8: ${e.message}`);
                    }
                }
                
                // 如果是视频分段（.ts），根据名称判断
                if (url.includes('.ts')) {
                    // 视频分段难以判断总时长，放行
                    logger.debug(`Video segment passed: ${url}`);
                }
            }
        }
        
        // 默认放行
        $done({});
    }

    // 根据不同客户端执行
    try {
        handleRequest();
    } catch (e) {
        logger.info(`Error: ${e.message}`);
        $done({});
    }
})();
