"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const maintainChangelog = (change) => {
    const changelogPath = path_1.default.join(__dirname, 'changelog.json');
    const changelog = JSON.parse(fs_1.default.readFileSync(changelogPath, 'utf-8') || '[]');
    changelog.push(change);
    fs_1.default.writeFileSync(changelogPath, JSON.stringify(changelog, null, 2));
    console.log('Changelog maintained.');
};
exports.default = maintainChangelog;
