export type ChannelId = 'google' | 'meta' | 'tiktok' | 'linkedin' | 'amazon' | 'bing' | 'x' | 'email' | 'seo';

export type ChannelDef = {
  id: ChannelId;
  label: string;
  color: string;   // tailwind color token you’ll apply
  hasStructure?: boolean;
  hasAssets?: boolean;
  hasInsights?: boolean;
  weight?: number; // contribution to completeness
};

export const CHANNELS: ChannelDef[] = [
  { id: 'google',  label: 'Google Ads',  color: 'bg-red-500',    hasStructure: true, hasAssets: true, hasInsights: true, weight: 24 },
  { id: 'meta',    label: 'Meta Ads',    color: 'bg-blue-600',   hasStructure: true, hasAssets: true, hasInsights: true, weight: 14 },
  { id: 'tiktok',  label: 'TikTok Ads',  color: 'bg-black',      hasStructure: true, hasAssets: true, hasInsights: true, weight: 8  },
  { id: 'linkedin',label: 'LinkedIn Ads',color: 'bg-sky-700',    hasStructure: true, hasAssets: true, hasInsights: true, weight: 6  },
  { id: 'amazon',  label: 'Amazon Ads',  color: 'bg-amber-600',  hasStructure: true, hasAssets: true, hasInsights: true, weight: 6  },
  { id: 'bing',    label: 'Bing Ads',    color: 'bg-indigo-600', hasStructure: true, hasAssets: true, hasInsights: true, weight: 4  },
  { id: 'x',       label: 'X Ads',       color: 'bg-neutral-800',hasStructure: true, hasAssets: true, hasInsights: true, weight: 4  },
  { id: 'email',   label: 'Email',       color: 'bg-emerald-600',hasStructure: false,hasAssets: true,  hasInsights: false,weight: 2  },
  { id: 'seo',     label: 'SEO',         color: 'bg-lime-600',   hasStructure: true, hasAssets: false, hasInsights: true, weight: 6  },
];

export const getChannel = (id: ChannelId) => CHANNELS.find(c => c.id === id);
