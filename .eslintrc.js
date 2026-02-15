/**
 * 腾讯代码规范 - ESLint 配置
 * 遵循 AlloyTeam 前端代码规范
 * @see http://alloyteam.github.io/CodeGuide/
 */
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'off',

    // 缩进：2 空格
    'indent': ['error', 2, { 'SwitchCase': 1 }],

    // 引号：单引号
    'quotes': ['error', 'single', { 'avoidEscape': true, 'allowTemplateLiterals': true }],

    // 分号：必须
    'semi': ['error', 'always'],

    // 空行限制
    'no-multiple-empty-lines': ['error', { 'max': 2, 'maxEOF': 1 }],

    // 行尾空格
    'no-trailing-spaces': 'error',

    // 文件末尾换行
    'eol-last': ['error', 'always'],

    // 逗号后不换行
    'comma-dangle': ['error', 'never'],

    // 对象大括号内不加空格
    'object-curly-spacing': ['error', 'never'],

    // 数组中括号内不加空格
    'array-bracket-spacing': ['error', 'never'],

    // 中缀运算符两侧空格
    'space-infix-ops': 'error',

    // 代码块前空格
    'space-before-blocks': 'error',

    // 关键字前后空格
    'keyword-spacing': ['error', { 'before': true, 'after': true }],

    // 逗号后空格
    'comma-spacing': ['error', { 'before': false, 'after': true }],

    // 对象冒号后空格
    'key-spacing': ['error', { 'beforeColon': false, 'afterColon': true }],

    // 使用 === 而非 ==
    'eqeqeq': ['error', 'always'],

    // 必须使用大括号
    'curly': ['error', 'all'],

    // 大括号风格
    'brace-style': ['error', '1tbs', { 'allowSingleLine': false }],

    // 禁止空代码块
    'no-empty': 'error',

    // 禁止 debugger
    'no-debugger': 'error',

    // 优先使用 const
    'prefer-const': 'error',

    // 禁止 var
    'no-var': 'error',

    // 箭头函数空格
    'arrow-spacing': ['error', { 'before': true, 'after': true }],

    // 箭头函数参数括号
    'arrow-parens': ['error', 'avoid'],

    // 行长度警告
    'max-len': ['warn', { 'code': 120, 'ignoreUrls': true }],

    // 代码块内不加空行
    'padded-blocks': ['error', 'never'],

    // 函数括号前不加空格
    'space-before-function-paren': ['error', {
      'anonymous': 'never',
      'named': 'never',
      'asyncArrow': 'always',
    }],

    // 禁止多个空格
    'no-multi-spaces': 'error',

    // 代码块内部空格
    'block-spacing': 'error',

    // 计算属性不加空格
    'computed-property-spacing': ['error', 'never'],

    // 函数调用括号前不加空格
    'func-call-spacing': ['error', 'never'],

    // 禁止混用空格和 Tab
    'no-mixed-spaces-and-tabs': 'error',
  },

  // TypeScript 配置
  overrides: [
    {
      files: ['*.ts', '*.tsx'],
      parser: '@typescript-eslint/parser',
      plugins: ['@typescript-eslint'],
      extends: [
        'eslint:recommended',
        '@typescript-eslint/recommended',
      ],
      rules: {
        '@typescript-eslint/no-unused-vars': 'warn',
        '@typescript-eslint/no-explicit-any': 'warn',

        // TypeScript 命名规范
        '@typescript-eslint/naming-convention': [
          'warn',
          {
            'selector': 'variable',
            'format': ['camelCase', 'UPPER_CASE', 'PascalCase'],
            'leadingUnderscore': 'allow',
            'trailingUnderscore': 'allow',
          },
          {
            'selector': 'function',
            'format': ['camelCase', 'PascalCase'],
          },
          {
            'selector': 'parameter',
            'format': ['camelCase'],
            'leadingUnderscore': 'allow',
          },
          {
            'selector': 'property',
            'format': null,
          },
          {
            'selector': 'memberLike',
            'modifiers': ['private'],
            'format': ['camelCase'],
            'leadingUnderscore': 'require',
          },
          {
            'selector': 'typeLike',
            'format': ['PascalCase'],
          },
        ],
      },
    },
  ],
};
