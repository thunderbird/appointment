/**
 * Enforce some globals like timezone for tests
 */
export const setup = () => {
  process.env.TZ = 'America/Vancouver';
};
