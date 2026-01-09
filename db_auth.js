// MongoDB Authentication Setup Script
// Run with: mongosh < db_auth.js

// Switch to admin database
use admin

// Create admin user (if not exists)
try {
    db.createUser({
        user: "boutiqueAdmin",
        pwd: "SecurePassword123!",
        roles: [
            { role: "userAdminAnyDatabase", db: "admin" }
        ]
    });
    print("✅ Admin user created");
} catch (e) {
    print("ℹ️  Admin user may already exist: " + e.message);
}

// Switch to BoutiqueComplete1 database
use BoutiqueComplete1

// Create application user with readWrite role
try {
    db.createUser({
        user: "boutiqueUser",
        pwd: "BoutiquePass2024!",
        roles: [
            { role: "readWrite", db: "BoutiqueComplete1" }
        ]
    });
    print("✅ Application user 'boutiqueUser' created with readWrite role on BoutiqueComplete1");
} catch (e) {
    print("ℹ️  User may already exist: " + e.message);
}

// Test authentication
print("\n📋 Existing users in BoutiqueComplete1:");
var usersResult = db.getUsers();
if (usersResult && usersResult.users) {
    usersResult.users.forEach(function (user) {
        print("   - " + user.user + ": " + JSON.stringify(user.roles));
    });
} else {
    print("   (No users found or unable to list users)");
}

print("\n✅ Authentication setup complete!");
print("\n🔐 To test authentication, restart MongoDB with --auth flag and connect with:");
print('   mongosh -u boutiqueUser -p "BoutiquePass2024!" --authenticationDatabase BoutiqueComplete1');
