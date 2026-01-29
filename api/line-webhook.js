/**
 * LINE Webhook API - 接收 LINE 事件並回覆新聞
 * 
 * 流程：
 * 1. LINE 平台收到群組訊息
 * 2. LINE call 這個 webhook
 * 3. 如果訊息是 /news，回覆最新新聞
 * 
 * 環境變數：
 * - LINE_CHANNEL_ACCESS_TOKEN: LINE Bot Access Token
 * - LINE_CHANNEL_SECRET: LINE Bot Channel Secret
 */

import crypto from 'crypto';

const LINE_REPLY_API = 'https://api.line.me/v2/bot/message/reply';

// 驗證 LINE 簽名
function validateSignature(body, signature, secret) {
  const hash = crypto
    .createHmac('SHA256', secret)
    .update(body)
    .digest('base64');
  return hash === signature;
}

// 取得最新新聞
async function getLatestNews() {
  try {
    const res = await fetch('https://thinkercafe-tw.github.io/thinker-news/latest.json');
    if (!res.ok) return null;
    const data = await res.json();
    return data.line_content;
  } catch (e) {
    console.error('Failed to fetch news:', e);
    return null;
  }
}

// 回覆訊息
async function replyMessage(replyToken, text, token) {
  const response = await fetch(LINE_REPLY_API, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      replyToken,
      messages: [{
        type: 'text',
        text
      }]
    })
  });
  return response.ok;
}

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Line-Signature');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // GET: 健康檢查
  if (req.method === 'GET') {
    return res.status(200).json({
      status: 'ok',
      message: 'LINE Bot Webhook is running'
    });
  }

  // POST: LINE Webhook
  if (req.method === 'POST') {
    const token = process.env.LINE_CHANNEL_ACCESS_TOKEN;
    const secret = process.env.LINE_CHANNEL_SECRET;

    if (!token || !secret) {
      console.error('Missing LINE credentials');
      return res.status(500).json({ error: 'Server configuration error' });
    }

    // 驗證簽名（可選，增加安全性）
    const signature = req.headers['x-line-signature'];
    const body = JSON.stringify(req.body);
    
    if (signature && !validateSignature(body, signature, secret)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    // 處理事件
    const events = req.body?.events || [];
    
    for (const event of events) {
      if (event.type !== 'message' || event.message?.type !== 'text') {
        continue;
      }

      const text = event.message.text.trim().toLowerCase();
      const replyToken = event.replyToken;

      // 觸發詞：/news 或 news
      if (text === '/news' || text === 'news') {
        const news = await getLatestNews();
        
        if (news) {
          await replyMessage(replyToken, news, token);
        } else {
          await replyMessage(replyToken, '❌ 無法取得今日新聞，請稍後再試', token);
        }
      }
    }

    return res.status(200).json({ status: 'ok' });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
