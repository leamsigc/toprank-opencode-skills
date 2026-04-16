import type { Plugin, Skill } from '@opencode-ai/plugin';

const skills: Skill[] = [
  {
    name: 'ads',
    path: './skills/ads',
    triggers: ['/toprank:ads'],
  },
  {
    name: 'seo-analysis',
    path: './skills/seo-analysis',
    triggers: ['/toprank:seo-analysis'],
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