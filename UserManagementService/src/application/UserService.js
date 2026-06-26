const User = require('../domain/User');

class UserService {
  constructor(userRepository) {
    this.userRepository = userRepository;
  }

  async registerUser(username, password) {
    const passwordHash = await this.authService.hashPassword(password);
    const user = new User({ username, passwordHash });
    return await this.userRepository.save(user);
  }

  async authenticateUser(username, password) {
    const user = await this.userRepository.findByUsername(username);
    if (!user) throw new Error('User not found');

    if (await this.authService.verifyPassword(password, user.passwordHash)) {
      return this.authService.generateToken(user);
    } else {
      throw new Error('Invalid credentials');
    }
  }
}

module.exports = UserService;
