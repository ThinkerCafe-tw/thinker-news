/**
 * 思考者暗門 - 隱藏入口機制
 * 在公開新聞頁面中嵌入的 JavaScript 模組
 */

class ThinkerSecretEntrance {
    constructor() {
        this.secretSequence = ['t', 'h', 'i', 'n', 'k', 'e', 'r']; // 按順序輸入 "thinker"
        this.userSequence = [];
        this.resetTimeout = null;
        this.isActivated = false;
        
        this.init();
    }
    
    init() {
        // 監聽鍵盤事件
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // 隱藏版：三次點擊特定元素
        this.createHiddenClickTrigger();
        
        // 開發模式提示
        if (this.isDevelopmentMode()) {
            console.log('🔧 開發提示：輸入 "thinker" 或連續點擊標題3次進入思考者模式');
        }
    }
    
    handleKeyPress(event) {
        // 忽略在輸入框中的按鍵
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }
        
        const key = event.key.toLowerCase();
        
        // 檢查是否為序列中的下一個字母
        if (key === this.secretSequence[this.userSequence.length]) {
            this.userSequence.push(key);
            
            // 清除重置計時器
            if (this.resetTimeout) {
                clearTimeout(this.resetTimeout);
            }
            
            // 設置新的重置計時器（2秒內沒有正確按鍵就重置）
            this.resetTimeout = setTimeout(() => {
                this.userSequence = [];
            }, 2000);
            
            // 檢查是否完成序列
            if (this.userSequence.length === this.secretSequence.length) {
                this.activateSecretMode();
            }
        } else {
            // 錯誤按鍵，重置序列
            this.userSequence = [];
            if (this.resetTimeout) {
                clearTimeout(this.resetTimeout);
            }
        }
    }
    
    createHiddenClickTrigger() {
        // 找到標題元素
        const titleElement = document.querySelector('.article-title, h1');
        if (titleElement) {
            let clickCount = 0;
            let clickTimeout = null;
            
            titleElement.addEventListener('click', (e) => {
                clickCount++;
                
                if (clickTimeout) {
                    clearTimeout(clickTimeout);
                }
                
                if (clickCount === 3) {
                    // 三次點擊，激活暗門
                    this.activateSecretMode();
                    clickCount = 0;
                } else {
                    // 設置重置計時器
                    clickTimeout = setTimeout(() => {
                        clickCount = 0;
                    }, 1000);
                }
            });
            
            // 添加微妙的視覺提示（只有知道的人才會注意到）
            titleElement.style.cursor = 'pointer';
            titleElement.style.userSelect = 'none';
        }
    }
    
    activateSecretMode() {
        if (this.isActivated) return;
        
        this.isActivated = true;
        this.userSequence = [];
        
        // 創建暗門入口按鈕
        this.createSecretButton();
        
        // 視覺反饋
        this.showActivationFeedback();
    }
    
    createSecretButton() {
        // 檢查是否已經存在按鈕
        if (document.getElementById('thinkerSecretBtn')) return;
        
        const button = document.createElement('div');
        button.id = 'thinkerSecretBtn';
        button.innerHTML = '🧠';
        button.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            width: 50px;
            height: 50px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            opacity: 0;
            transform: scale(0);
            animation: secretButtonAppear 0.5s ease forwards;
        `;
        
        // 添加動畫樣式
        const style = document.createElement('style');
        style.textContent = `
            @keyframes secretButtonAppear {
                to {
                    opacity: 1;
                    transform: scale(1);
                }
            }
            
            @keyframes secretPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            #thinkerSecretBtn:hover {
                animation: secretPulse 0.6s ease infinite;
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
        `;
        document.head.appendChild(style);
        
        // 點擊事件
        button.addEventListener('click', () => {
            this.openThinkerPanel();
        });
        
        document.body.appendChild(button);
        
        // 10秒後自動隱藏（防止被意外發現）
        setTimeout(() => {
            if (button.parentNode) {
                button.style.animation = 'secretButtonAppear 0.5s ease reverse forwards';
                setTimeout(() => {
                    if (button.parentNode) {
                        button.remove();
                    }
                }, 500);
            }
        }, 10000);
    }
    
    showActivationFeedback() {
        // 創建短暫的視覺反饋
        const feedback = document.createElement('div');
        feedback.textContent = '🧠 思考者模式已激活';
        feedback.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            font-weight: 600;
            z-index: 10001;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: feedbackAppear 2s ease forwards;
        `;
        
        const feedbackStyle = document.createElement('style');
        feedbackStyle.textContent = `
            @keyframes feedbackAppear {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                20% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            }
        `;
        document.head.appendChild(feedbackStyle);
        
        document.body.appendChild(feedback);
        
        // 2秒後移除
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 2000);
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