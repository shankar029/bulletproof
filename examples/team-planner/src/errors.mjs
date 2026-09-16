export class AppError extends Error {
  constructor(code, message, status = 400, field) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.status = status;
    this.field = field;
  }
}

export function invalid(message, field) {
  throw new AppError('INVALID_INPUT', message, 400, field);
}
