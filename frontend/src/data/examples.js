export const blankTransaction = {
  transaction_id: '',
  timestamp: new Date().toISOString(),
  type: 'transfer',
  amount: 0,
  counterparty: '',
  status: 'completed'
};

export const sampleCases = [
  {
    label: 'Wrong transfer',
    payload: {
      ticket_id: 'TKT-001',
      complaint: "I sent 5000 taka to a wrong number around 2pm today. The number was supposed to be 01712345678 but I think I typed it wrong. The person isn't responding to my call. Please help me get my money back.",
      language: 'en',
      channel: 'in_app_chat',
      user_type: 'customer',
      campaign_context: 'boishakh_bonanza_day_1',
      transaction_history: [
        {
          transaction_id: 'TXN-9101',
          timestamp: '2026-04-14T14:08:22Z',
          type: 'transfer',
          amount: 5000,
          counterparty: '+8801719876543',
          status: 'completed'
        },
        {
          transaction_id: 'TXN-9087',
          timestamp: '2026-04-13T18:12:00Z',
          type: 'cash_in',
          amount: 10000,
          counterparty: 'AGENT-512',
          status: 'completed'
        }
      ],
      metadata: {}
    }
  },
  {
    label: 'Failed payment',
    payload: {
      ticket_id: 'TKT-002',
      complaint: 'My payment of 1250 BDT failed but my balance was deducted. Please check the payment to MERCHANT-220.',
      language: 'en',
      channel: 'web_portal',
      user_type: 'customer',
      campaign_context: '',
      transaction_history: [
        {
          transaction_id: 'TXN-7201',
          timestamp: '2026-04-15T09:22:11Z',
          type: 'payment',
          amount: 1250,
          counterparty: 'MERCHANT-220',
          status: 'failed'
        }
      ],
      metadata: {}
    }
  },
  {
    label: 'Phishing risk',
    payload: {
      ticket_id: 'TKT-003',
      complaint: 'Someone called me and asked for my OTP and PIN to unlock a cashback offer. I think it is suspicious.',
      language: 'en',
      channel: 'phone_support',
      user_type: 'customer',
      campaign_context: 'cashback_campaign',
      transaction_history: [],
      metadata: { risk_signal: 'credential_request' }
    }
  }
];

export const transactionTypes = ['transfer', 'payment', 'cash_in', 'cash_out', 'settlement', 'refund'];
export const transactionStatuses = ['completed', 'failed', 'pending', 'reversed'];
export const languageOptions = ['en', 'bn', 'mixed'];
export const userTypes = ['customer', 'merchant', 'agent', 'unknown'];
