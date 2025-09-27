/**
 * 思考者入口 - 簡單直接的入口按鈕
 * 在公開新聞頁面底部添加思考者入口按鈕
 */

class ThinkerSecretEntrance {
    constructor() {
        this.password = 'thinker';
        this.isActivated = false;
        this.init();
    }
    
    init() {
        // 等待頁面載入完成後添加按鈕
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.createThinkerButton());
        } else {
            this.createThinkerButton();
        }
        
        // 開發模式提示
        if (this.isDevelopmentMode()) {
            console.log('🧠 思考者入口已載入，密碼：thinker');
        }
    }
    
    createThinkerButton() {
        // 尋找插入位置
        let targetElement = null;
        
        // 首頁：尋找包含 "🚀 讓複雜的 AI 世界變得簡單易懂" 的區域
        const homeElements = document.querySelectorAll('*');
        for (let el of homeElements) {
            if (el.textContent && el.textContent.includes('🚀 讓複雜的 AI 世界變得簡單易懂')) {
                targetElement = el.closest('.container, .footer, .intro-section') || el.parentElement;
                break;
            }
        }
        
        // 新聞頁面：尋找包含 "🏠 返回首頁" 的區域
        if (!targetElement) {
            for (let el of homeElements) {
                if (el.textContent && el.textContent.includes('🏠 返回首頁')) {
                    targetElement = el.closest('.footer-nav, .nav-section') || el.parentElement;
                    break;
                }
            }
        }
        
        // 如果都找不到，就放在頁面最底部
        if (!targetElement) {
            targetElement = document.body;
        }
        
        // 創建思考者入口按鈕
        const thinkerButton = document.createElement('a');
        thinkerButton.id = 'thinkerEntrance';
        thinkerButton.href = '#';
        thinkerButton.innerHTML = '🧠 思考者入口';
        thinkerButton.style.cssText = `
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            margin: 0 10px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        `;
        
        // 點擊事件
        thinkerButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.promptPassword();
        });
        
        // 懸停效果
        thinkerButton.addEventListener('mouseenter', () => {
            thinkerButton.style.background = 'rgba(255, 255, 255, 0.3)';
            thinkerButton.style.transform = 'translateY(-2px)';
        });
        
        thinkerButton.addEventListener('mouseleave', () => {
            thinkerButton.style.background = 'rgba(255, 255, 255, 0.2)';
            thinkerButton.style.transform = 'translateY(0)';
        });
        
        // 添加到頁面
        if (targetElement === document.body) {
            // 如果是添加到 body，創建一個固定底部的容器
            const footer = document.createElement('div');
            footer.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
            `;
            footer.appendChild(thinkerButton);
            document.body.appendChild(footer);
        } else {
            // 添加到現有的導航區域
            targetElement.appendChild(thinkerButton);
        }
        
        if (this.isDevelopmentMode()) {
            console.log('🧠 思考者入口按鈕已添加');
        }
    }
    
    promptPassword() {
        const password = prompt('🧠 歡迎來到思考者入口\n\n請輸入密碼：');
        
        if (password === this.password) {
            this.openThinkerPanel();
        } else if (password !== null) {
            alert('❌ 密碼錯誤\n\n提示：密碼就是 "thinker"');
        }
    }
    
    openThinkerPanel() {
        // 檢查是否為同域名
        const panelUrl = this.getThinkerPanelUrl();
        
        // 在新標籤頁中打開思考者面板
        const newWindow = window.open(panelUrl, '_blank', 'width=1200,height=800');
        
        if (!newWindow) {
            // 如果彈窗被阻擋，提供備用方案
            this.showPanelModal();
        }
    }
    
    getThinkerPanelUrl() {
        // 根據當前環境決定面板 URL
        const currentDomain = window.location.origin;
        
        if (this.isDevelopmentMode()) {
            return `${currentDomain}/thinker_private_panel.html`;
        } else {
            // 生產環境中的面板位置
            return `${currentDomain}/private/thinker_panel.html`;
        }
    }
    
    showPanelModal() {
        // 備用方案：在當前頁面顯示模態框
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10002;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const iframe = document.createElement('iframe');
        iframe.src = this.getThinkerPanelUrl();
        iframe.style.cssText = `
            width: 90%;
            height: 90%;
            max-width: 1200px;
            border: none;
            border-radius: 20px;
            background: white;
        `;
        
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕';
        closeBtn.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            z-index: 10003;
        `;
        
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        modal.appendChild(iframe);
        modal.appendChild(closeBtn);
        document.body.appendChild(modal);
    }
    
    isDevelopmentMode() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.hostname.includes('dev');
    }
    
    // 公共API，供其他腳本調用
    static initSecretEntrance() {
        if (!window.thinkerEntrance) {
            window.thinkerEntrance = new ThinkerSecretEntrance();
        }
        return window.thinkerEntrance;
    }
}

// 自動初始化（除非明確禁用）
if (!window.DISABLE_THINKER_ENTRANCE) {
    // 等待 DOM 加載完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            ThinkerSecretEntrance.initSecretEntrance();
        });
    } else {
        ThinkerSecretEntrance.initSecretEntrance();
    }
}

// 導出供模組化使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThinkerSecretEntrance;
}