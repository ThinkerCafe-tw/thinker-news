/**
 * Debug API - 檢查環境變數設定狀態
 */

export default function handler(req, res) {
  const lineToken = process.env.LINE_CHANNEL_ACCESS_TOKEN || '';
  const lineSecret = process.env.LINE_CHANNEL_SECRET || '';
  const groupIds = process.env.LINE_GROUP_IDS || '';

  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    env_check: {
      LINE_CHANNEL_ACCESS_TOKEN: {
        exists: !!lineToken,
        length: lineToken.length,
        first_10_chars: lineToken.substring(0, 10) || null
      },
      LINE_CHANNEL_SECRET: {
        exists: !!lineSecret,
        length: lineSecret.length,
        first_10_chars: lineSecret.substring(0, 10) || null
      },
      LINE_GROUP_IDS: {
        exists: !!groupIds,
        count: groupIds ? groupIds.split(',').length : 0
      }
    }
  });
}
