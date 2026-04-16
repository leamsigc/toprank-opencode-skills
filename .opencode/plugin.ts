import type { Plugin, Skill } from '@opencode-ai/plugin';

const skills: Skill[] = [
  {
    name: 'ads',
    path: './google-ads/ads',
    triggers: ['/toprank:ads', 'google ads', 'campaigns', 'keywords', 'ad spend', 'CPA', 'ROAS'],
  },
  {
    name: 'ads-audit',
    path: './google-ads/ads-audit',
    triggers: ['/toprank:ads-audit', 'ads audit'],
  },
  {
    name: 'ads-copy',
    path: './google-ads/ads-copy',
    triggers: ['/toprank:ads-copy', 'ad copy'],
  },
  {
    name: 'seo-analysis',
    path: './seo/seo-analysis',
    triggers: ['/toprank:seo-analysis', 'seo analysis', 'SEO audit', 'technical SEO'],
  },
  {
    name: 'content-writer',
    path: './seo/content-writer',
    triggers: ['/toprank:content-writer', 'content writer'],
  },
  {
    name: 'keyword-research',
    path: './seo/keyword-research',
    triggers: ['/toprank:keyword-research', 'keyword research'],
  },
  {
    name: 'meta-tags-optimizer',
    path: './seo/meta-tags-optimizer',
    triggers: ['/toprank:meta-tags-optimizer', 'meta tags'],
  },
  {
    name: 'schema-markup-generator',
    path: './seo/schema-markup-generator',
    triggers: ['/toprank:schema-markup-generator', 'schema markup'],
  },
  {
    name: 'setup-cms',
    path: './seo/setup-cms',
    triggers: ['/toprank:setup-cms', 'setup cms'],
  },
  {
    name: 'toprank-upgrade-skill',
    path: './toprank-upgrade-skill',
    triggers: ['/toprank:upgrade', 'upgrade toprank'],
  },
  {
    name: 'gemini',
    path: './gemini',
    triggers: ['/toprank:gemini', 'gemini'],
  },
];

export const plugin: Plugin = {
  name: 'toprank',
  version: '1.0.0',
  skills,
  hooks: {
    onLoad: async () => {
      console.log('Toprank plugin loaded');
    },
  },
};

export default plugin;