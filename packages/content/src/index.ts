import english from "./locales/en.json";
import spanish from "./locales/es.json";

export type Locale = "en" | "es";

export const contentByLocale = {
  en: english,
  es: spanish
} satisfies Record<Locale, typeof english>;

export const release = {
  version: english.thesis.version,
  tag: `v${english.thesis.version}`,
  trackerUrl: `https://github.com/edwardcalderon/Master-s-thesis/releases/tag/v${english.thesis.version}`
} as const;
