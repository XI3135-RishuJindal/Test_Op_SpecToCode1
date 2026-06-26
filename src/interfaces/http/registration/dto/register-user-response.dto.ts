import { ApiProperty } from '@nestjs/swagger';

export class RegisterUserResponseDto {
  @ApiProperty({ example: '550e8400-e29b-41d4-a716-446655440000' })
  userId: string;

  @ApiProperty({ example: 'PENDING_VERIFICATION' })
  status: string;

  @ApiProperty({ example: 'Registration successful. Please verify your email.' })
  message: string;
}
