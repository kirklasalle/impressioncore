"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const trackTask = (task) => {
    const tasksPath = path_1.default.join(__dirname, 'tasks.json');
    const tasks = JSON.parse(fs_1.default.readFileSync(tasksPath, 'utf-8') || '[]');
    tasks.push(task);
    fs_1.default.writeFileSync(tasksPath, JSON.stringify(tasks, null, 2));
    console.log('Task progress tracked.');
};
exports.default = trackTask;
