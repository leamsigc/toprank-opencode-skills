import type { Skill } from '@opencode-ai/plugin';

export const adsSkill: Skill = {
  name: 'ads',
  path: './skills/ads',
  triggers: ['/toprank:ads'],
};

export const seoAnalysisSkill: Skill = {
  name: 'seo-analysis',
  path: './skills/seo-analysis',
  triggers: ['/toprank:seo-analysis'],
};

export const skills: Skill[] = [adsSkill, seoAnalysisSkill];
export { adsSkill, seoAnalysisSkill };