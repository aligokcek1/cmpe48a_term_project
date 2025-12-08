#!/bin/bash
# Script to populate MongoDB using mongosh directly on the VM
# Usage: ./scripts/populate_atms_mongosh.sh [MONGODB_PASSWORD]

set -e

MONGODB_PASSWORD=${1:-123456789}

echo "🚀 Populating ATM database using mongosh..."

# Copy JSON file to VM
echo "📤 Copying ATM data to VM..."
gcloud compute scp atm-locator/config/atm_data.json mongodb-vm:~/atm_data.json --zone=us-central1-a

# Create a JavaScript script to import the data
echo "📝 Creating import script..."
cat > /tmp/import_atms.js << 'IMPORTSCRIPT'
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/home/aligokcek1/atm_data.json', 'utf8'));

// Connect to database
db = db.getSiblingDB('bank');

// Clear existing ATMs
print('🗑️  Clearing existing ATMs...');
db.atms.deleteMany({});

// Process and insert ATMs
print('💾 Inserting ATM data...');
const atms = data.map(item => {
  const atm = {
    _id: ObjectId(item._id.$oid),
    name: item.name,
    address: item.address,
    coordinates: item.coordinates,
    timings: item.timings,
    atmHours: item.atmHours,
    numberOfATMs: item.numberOfATMs,
    isOpen: item.isOpen,
    interPlanetary: item.interPlanetary || false,
    createdAt: new Date(item.createdAt.$date),
    updatedAt: new Date(item.updatedAt.$date)
  };
  return atm;
});

const result = db.atms.insertMany(atms);
print(`✅ Inserted ${result.insertedIds.length} ATMs`);

// Verify
const total = db.atms.countDocuments({});
const open = db.atms.countDocuments({isOpen: true});
const interplanetary = db.atms.countDocuments({interPlanetary: true});

print('\n📊 Database Status:');
print(`   Total ATMs: ${total}`);
print(`   Open ATMs: ${open}`);
print(`   Interplanetary ATMs: ${interplanetary}`);

// Show sample
const sample = db.atms.findOne();
if (sample) {
  print(`\n📍 Sample ATM: ${sample.name}`);
  print(`   Address: ${sample.address.street}, ${sample.address.city}`);
}
IMPORTSCRIPT

# Copy the import script to VM
gcloud compute scp /tmp/import_atms.js mongodb-vm:~/import_atms.js --zone=us-central1-a

# Run the import script
echo "▶️  Running import script..."
gcloud compute ssh mongodb-vm --zone=us-central1-a --command="
    mongosh -u root -p $MONGODB_PASSWORD --authenticationDatabase admin --host 10.128.0.2:27017 ~/import_atms.js
"

# Cleanup
rm -f /tmp/import_atms.js

echo "✅ Done!"
