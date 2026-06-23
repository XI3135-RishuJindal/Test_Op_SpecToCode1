import { Controller, Post, Body, HttpCode, HttpStatus, Version } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { RegisterUserDto } from './dto/register-user.dto';
import { RegisterUserUseCase } from '../../../application/registration/use-cases/register-user.use-case';

@ApiTags('Registration')
@Controller('registration')
export class RegistrationController {
  constructor(private readonly registerUserUseCase: RegisterUserUseCase) {}

  @Post()
  @Version('1')
  @HttpCode(HttpStatus.ACCEPTED)
  @ApiOperation({ summary: 'Register a new user account' })
  @ApiResponse({ status: 202, description: 'Registration accepted. Verification email sent.' })
  @ApiResponse({ status: 400, description: 'Validation error' })
  @ApiResponse({ status: 409, description: 'Email already registered (generic response)' })
  async register(@Body() dto: RegisterUserDto): Promise<{ message: string }> {
    await this.registerUserUseCase.execute({
      email: dto.email,
      password: dto.password,
      idempotencyKey: dto.idempotencyKey,
      captchaToken: dto.captchaToken,
    });
    // Generic response to prevent user enumeration
    return { message: 'If this email is not already registered, a verification link has been sent.' };
  }
}
