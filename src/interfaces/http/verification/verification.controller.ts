import { Controller, Post, Body, HttpCode, HttpStatus, Version } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { VerifyEmailDto } from './dto/verify-email.dto';
import { VerifyEmailUseCase } from '../../../application/verification/use-cases/verify-email.use-case';

@ApiTags('Verification')
@Controller('verification')
export class VerificationController {
  constructor(private readonly verifyEmailUseCase: VerifyEmailUseCase) {}

  @Post('email')
  @Version('1')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Verify email address using a token' })
  @ApiResponse({ status: 200, description: 'Email verified successfully.' })
  @ApiResponse({ status: 400, description: 'Invalid or expired token (generic)' })
  async verifyEmail(@Body() dto: VerifyEmailDto): Promise<{ message: string }> {
    await this.verifyEmailUseCase.execute({ token: dto.token });
    // Generic response to prevent enumeration
    return { message: 'Email verification processed.' };
  }
}
