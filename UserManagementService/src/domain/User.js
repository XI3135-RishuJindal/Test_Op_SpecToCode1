class User {
  constructor({ id, username, passwordHash }) {
    this.id = id;
    this.username = username;
    this.passwordHash = passwordHash;
  }

  // Other relevant domain methods can be added here
}

module.exports = User;
