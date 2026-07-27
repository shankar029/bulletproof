// Reusable, framework-free validation rules shared across the app.
export const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

/** Returns the first password problem message, or '' when the password is strong. */
export const passwordProblem = (pw) => {
  if (pw.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Za-z]/.test(pw) || !/\d/.test(pw)) return 'Password needs a letter and a number';
  return '';
};
