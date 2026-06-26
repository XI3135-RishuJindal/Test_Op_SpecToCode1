const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

class AuthService {
  async hashPassword(password) {
    return await bcrypt.hash(password, 10);
  }

  async verifyPassword(password, passwordHash) {
    return await bcrypt.compare(password, passwordHash);
  }

  generateToken(user) {
    return jwt.sign({ id: user.id, username: user.username }, process.env.JWT_SECRET, { expiresIn: '1h' });
  }
}

module.exports = AuthService;
