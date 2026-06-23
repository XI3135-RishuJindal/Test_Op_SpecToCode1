import { IsString, IsNotEmpty, MaxLength } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class VerifyEmailDto {
  @ApiProperty({ description: 'Raw verification token sent to the user via email' })
  @IsString()
  @IsNotEmpty()
  @MaxLength(512)
  token: string;
}
