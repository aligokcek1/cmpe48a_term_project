/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

const functions = require('@google-cloud/functions-framework');
const { MongoClient } = require('mongodb');

const DB_URL = process.env.DB_URL || 'mongodb://root:123456789@10.128.0.2:27017/bank?authSource=admin';

let cachedDb = null;

async function connectToDatabase() {
    if (cachedDb) {
        return cachedDb;
    }

    const client = new MongoClient(DB_URL);
    await client.connect();
    cachedDb = client.db('bank');
    console.log('Connected to MongoDB');
    return cachedDb;
}

functions.http('atmLocator', async (req, res) => {
    // Set CORS headers
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.status(204).send('');
        return;
    }

    try {
        const db = await connectToDatabase();
        const atmsCollection = db.collection('atms');

        // Handle POST /api/atm - Get ATMs with filters
        if (req.method === 'POST') {
            let query = {
                interPlanetary: false,
            };

            if (req.body.isOpenNow) {
                query.isOpen = true;
            }
            if (req.body.isInterPlanetary) {
                query.interPlanetary = true;
            }

            const atms = await atmsCollection.find(query, {
                projection: {
                    name: 1,
                    coordinates: 1,
                    address: 1,
                    isOpen: 1,
                }
            }).toArray();

            // Shuffle and return 4 random ATMs
            const shuffledATMs = [...atms]
                .sort(() => Math.random() - 0.5)
                .slice(0, 4);

            if (shuffledATMs && shuffledATMs.length > 0) {
                res.status(200).json(shuffledATMs);
            } else {
                res.status(404).json({ error: 'No ATMs found' });
            }
        }
        // Handle GET /:id - Get specific ATM
        else if (req.method === 'GET') {
            const atmId = req.query.id || req.path.split('/').pop();

            if (!atmId) {
                res.status(400).json({ error: 'ATM ID is required' });
                return;
            }

            const ObjectId = require('mongodb').ObjectId;
            const atm = await atmsCollection.findOne({ _id: new ObjectId(atmId) });

            if (atm) {
                res.status(200).json({
                    coordinates: atm.coordinates,
                    timings: atm.timings,
                    atmHours: atm.atmHours,
                    numberOfATMs: atm.numberOfATMs,
                    isOpen: atm.isOpen,
                    interPlanetary: atm.interPlanetary || false,
                });
            } else {
                res.status(404).json({ error: 'ATM not found' });
            }
        } else {
            res.status(404).json({ error: 'Not found' });
        }
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: error.message });
    }
});
