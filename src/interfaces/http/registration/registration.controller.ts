import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  ConflictException,
  BadRequestException,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { RegisterUserDto } from './dto/register-user.dto';
import { RegisterUserResponseDto } from './dto/register-user-response.dto';
import { RegisterUserUseCase } from '../../../application/use-cases/register-user.use-case';

@ApiTags('Registration')
@Controller('api/v1/registrations')
export class RegistrationController {
  constructor(private readonly registerUserUseCase: RegisterUserUseCase) {}

  @Post()
  @HttpCode(HttpStatus.ACCEPTED)
  @ApiOperation({ summary: 'Register a new user account' })
  @ApiResponse({ status: 202, type: RegisterUserResponseDto })
  @ApiResponse({ status: 409, description: 'Email already registered (generic message)' })
  @ApiResponse({ status: 422, description: 'Validation error' })
  async register(@Body() dto: RegisterUserDto): Promise<RegisterUserResponseDto> {
    try {
      const result = await this.registerUserUseCase.execute({
        idempotencyKey: dto.idempotencyKey,
        email: dto.email,
        password: dto.password,
        captchaToken: dto.captchaToken,
      });

      return {
        userId: result.userId,
        status: result.status,
        // Generic message — prevents email enumeration
        message: 'If this email is not already registered, a verification link has been sent.',
      };
    } catch (err: any) {
      if (err?.status === 409) {
        // Return the same generic message to prevent enumeration
        throw new ConflictException(
          'If this email is not already registered, a verification link has been sent.',
        );
      }
      if (err instanceof Error && err.message.includes('Password')) {
        throw new BadRequestException(err.message);
      }
      throw err;
    }
  }
}
