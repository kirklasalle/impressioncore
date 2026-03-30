"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const storeData = (data) => {
    const dataPath = path_1.default.join(__dirname, 'data.json');
    fs_1.default.writeFileSync(dataPath, JSON.stringify(data, null, 2));
    console.log('Persistent data stored.');
};
exports.default = storeData;
