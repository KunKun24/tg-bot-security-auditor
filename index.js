import { fileURLToPath } from "node:url";
import { apply as applyFilesystemProvider } from "@deepseek-ai/dsh-skill-filesystem";

const skillsRoot = fileURLToPath(new URL("./skills/", import.meta.url));

export const name = "tg-bot-security-auditor";
export const inject = ["skills"];

/**
 * Register the bundled skill directory as a skill provider.
 * The skill itself (SKILL.md, rules/, references/, examples/) ships untouched
 * under ./skills/tg-bot-security-auditor/.
 */
export function apply(ctx) {
  applyFilesystemProvider(ctx, {
    providerName: name,
    includeDefaultRoots: false,
    bundledSkillDir: skillsRoot,
    watch: false,
  });
}
