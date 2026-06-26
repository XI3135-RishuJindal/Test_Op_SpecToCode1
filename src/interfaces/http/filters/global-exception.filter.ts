import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Response } from 'express';
import {
  DomainException,
  InvalidVerificationTokenException,
  UserAlreadyExistsException,
  AccountNotPendingVerificationException,
} from '../../../domain/exceptions/domain.exceptions';

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(GlobalExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    if (exception instanceof HttpException) {
      response.status(exception.getStatus()).json(exception.getResponse());
      return;
    }

    if (exception instanceof InvalidVerificationTokenException) {
      response.status(HttpStatus.BAD_REQUEST).json({
        statusCode: HttpStatus.BAD_REQUEST,
        message: 'Invalid or expired verification token.',
      });
      return;
    }

    if (exception instanceof UserAlreadyExistsException) {
      // Return generic 202 to prevent enumeration
      response.status(HttpStatus.ACCEPTED).json({
        message: 'If this email is not already registered, a verification link has been sent.',
      });
      return;
    }

    if (exception instanceof AccountNotPendingVerificationException) {
      response.status(HttpStatus.CONFLICT).json({
        statusCode: HttpStatus.CONFLICT,
        message: 'Account is not eligible for this operation.',
      });
      return;
    }

    if (exception instanceof DomainException) {
      response.status(HttpStatus.UNPROCESSABLE_ENTITY).json({
        statusCode: HttpStatus.UNPROCESSABLE_ENTITY,
        message: exception.message,
      });
      return;
    }

    this.logger.error('Unhandled exception', exception);
    response.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
      statusCode: HttpStatus.INTERNAL_SERVER_ERROR,
      message: 'An unexpected error occurred.',
    });
  }
}
