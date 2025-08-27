export type QuickReplyOption = {
  id: string
  label: string
  payload?: any // ex: { type: 'channel', value: 'google ads' } sau orice structură
}

export type QuickReplyGroup = {
  id: string              // ex: 'ask_channels', 'ask_website'
  title: string           // întrebarea afișată
  multi?: boolean         // permite multe selecții
  options: QuickReplyOption[]
  allowCustom?: boolean
  customPlaceholder?: string
}
