import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  BadRequestException,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { VerifyEmailDto } from './dto/verify-email.dto';
import { VerifyEmailResponseDto } from './dto/verify-email-response.dto';
import { VerifyEmailUseCase } from '../../../application/use-cases/verify-email.use-case';

@ApiTags('Verification')
@Controller('api/v1/verifications')
export class VerificationController {
  constructor(private readonly verifyEmailUseCase: VerifyEmailUseCase) {}

  @Post('email')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Verify email address using a one-time token' })
  @ApiResponse({ status: 200, type: VerifyEmailResponseDto })
  @ApiResponse({ status: 400, description: 'Invalid or expired token (generic message)' })
  async verifyEmail(@Body() dto: VerifyEmailDto): Promise<VerifyEmailResponseDto> {
    try {
      const result = await this.verifyEmailUseCase.execute({ token: dto.token });
      return {
        userId: result.userId,
        status: result.status,
        message: 'Email verified successfully. Your account is now active.',
      };
    } catch {
      // Generic error — prevents token enumeration
      throw new BadRequestException('The verification link is invalid or has expired.');
    }
  }
}
