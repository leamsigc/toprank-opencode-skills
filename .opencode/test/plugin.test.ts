import { describe, it, expect } from 'vitest';
import { plugin } from '../plugin';

describe('Toprank Plugin', () => {
  it('should load without errors', async () => {
    expect(plugin).toBeDefined();
    expect(plugin.name).toBe('toprank');
    expect(plugin.version).toBe('1.0.0');
  });

  it('should have skills defined', () => {
    expect(plugin.skills).toBeDefined();
    expect(plugin.skills.length).toBeGreaterThan(0);
  });

  it('should not contain blocked patterns', () => {
    const pluginCode = JSON.stringify(plugin);
    expect(pluginCode).not.toContain('opencode-openai-codex-auth');
  });
});