module.exports = {
    root: true,
    env: { browser: true, es2022: true },
    parserOptions: { ecmaVersion: 'latest', sourceType: 'module', ecmaFeatures: { jsx: true } },
    ignorePatterns: ['dist/', 'node_modules/'],
    rules: {
        'no-dupe-args': 'error',
        'no-dupe-keys': 'error',
        'no-unreachable': 'error',
        'no-invalid-regexp': 'error',
        'no-unexpected-multiline': 'error',
    },
    overrides: [{ files: ['*.config.js', '*.cjs', '*.mjs'], env: { node: true } }],
};
