---
title: linux内核代码规范
type: categories
categories: 通用技术
cover: "../images/封面.png"
description: Linux 内核代码规范
abbrlink: 66378cb
typora-root-url: ./..\..\..
date: 2022-10-29 00:00:00
swiper_index:
---
缩进：

使用 8 个空格的制表符进行缩进。
函数参数和长表达式在续行时也使用 8 个空格的缩进。
行长度：

每行最大长度为 80 个字符。
大括号：

大括号前换行，符合 Linux 风格。
空格：

赋值操作符前后留空格。
控制语句（如 if, for, while）前留空格。
行尾注释前留两个空格。
其他：

不允许短的 if 语句、循环语句、函数和代码块写在一行。
字符串字面量允许换行。
指针对齐方式为右对齐。
以下是调整后的 .clang-format 文件，确保更符合 Linux 内核的代码规范：
```shell
sudo apt install clang-format
```

```clang-format
---
BasedOnStyle: LLVM
IndentWidth: 8          # 通用缩进宽度为8个空格
UseTab: Never           # 不使用制表符，只使用空格
TabWidth: 8             # 制表符宽度为8个空格
ColumnLimit: 0
BreakBeforeBraces: Linux
AllowShortIfStatementsOnASingleLine: false
AllowShortLoopsOnASingleLine: false
AllowShortFunctionsOnASingleLine: None
AllowShortBlocksOnASingleLine: false
SpacesBeforeTrailingComments: 2
SpaceBeforeAssignmentOperators: true
SpaceBeforeParens: ControlStatements
SpaceInEmptyParentheses: false
AlwaysBreakTemplateDeclarations: Yes
BinPackParameters: false
BinPackArguments: false
AlignAfterOpenBracket: Align
AlignConsecutiveMacros: false
AlignConsecutiveBitFields: false
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
AlignEscapedNewlines: Left
AlignOperands: false
AlignTrailingComments: false
AllowAllParametersOfDeclarationOnNextLine: false
AllowAllArgumentsOnNextLine: false
BreakBeforeBinaryOperators: NonAssignment
BreakBeforeTernaryOperators: true
BreakStringLiterals: true
ConstructorInitializerAllOnOneLineOrOnePerLine: false
ConstructorInitializerIndentWidth: 0
ContinuationIndentWidth: 8
DerivePointerBinding: false
FixNamespaceComments: false
IncludeBlocks: Preserve
IndentCaseLabels: false
IndentPPDirectives: None
KeepEmptyLinesAtTheStartOfBlocks: false
MaxEmptyLinesToKeep: 1
NamespaceIndentation: All
PenaltyBreakBeforeFirstCallParameter: 19
PenaltyBreakComment: 300
PenaltyBreakString: 1000
PenaltyExcessCharacter: 1000000
PenaltyReturnTypeOnItsOwnLine: 60
PointerAlignment: Right
ReflowComments: false
SortIncludes: false
SortUsingDeclarations: false
SpaceAfterCStyleCast: false
SpaceAfterTemplateKeyword: false
SpaceBeforeCpp11BracedList: false
SpaceBeforeInheritanceColon: false
SpaceBeforeRangeBasedForLoopColon: false
Standard: Cpp11
UseCRLF: false
---

---
Language:        Cpp
AccessModifierOffset: -4 # 将访问控制符向左缩进8个空格
#IndentAccessModifiers: true  # 对访问控制符进行缩进
---

```

关键点解释
IndentWidth: 8: 使用 8 个空格的缩进。
UseTab: Always: 使用制表符而不是空格进行缩进。
TabWidth: 8: 制表符宽度为 8 个空格。
ColumnLimit: 80: 每行最大长度为 80 个字符。
BreakBeforeBraces: Linux: 在大括号前换行，符合 Linux 风格。
AllowShortIfStatementsOnASingleLine: false: 不允许短的 if 语句写在一行。
AllowShortLoopsOnASingleLine: false: 不允许短的循环语句写在一行。
AllowShortFunctionsOnASingleLine: None: 不允许短的函数写在一行。
AllowShortBlocksOnASingleLine: false: 不允许短的代码块写在一行。
SpacesBeforeTrailingComments: 2: 行尾注释前留两个空格。
SpaceBeforeAssignmentOperators: true: 赋值操作符前后留空格。
SpaceBeforeParens: ControlStatements: 控制语句（如 if, for, while）前留空格。
SpaceInEmptyParentheses: false: 空括号内不留空格。
AlwaysBreakTemplateDeclarations: Yes: 模板声明总是换行。
BinPackParameters: false: 参数列表不紧凑排列。
BinPackArguments: false: 函数调用参数不紧凑排列。
AlignAfterOpenBracket: Align: 开括号后不对齐。
AlignConsecutiveMacros: false: 连续的宏定义不对齐。
AlignConsecutiveBitFields: false: 连续的位字段不对齐。
AlignConsecutiveAssignments: false: 连续的赋值语句不对齐。
AlignConsecutiveDeclarations: false: 连续的声明不对齐。
AlignEscapedNewlines: Left: 转义的换行符左对齐。
AlignOperands: false: 操作数不对齐。
AlignTrailingComments: false: 行尾注释不对齐。
AllowAllParametersOfDeclarationOnNextLine: false: 函数声明的参数不允许全部放在下一行。
AllowAllArgumentsOnNextLine: false: 函数调用的参数不允许全部放在下一行。
AllowParameterAlignment: false: 参数不允许对齐。
BreakBeforeBinaryOperators: NonAssignment: 二元操作符前换行，但赋值操作符除外。
BreakBeforeTernaryOperators: true: 三元操作符前换行。
BreakStringLiterals: true: 字符串字面量允许换行。
ConstructorInitializerAllOnOneLineOrOnePerLine: false: 构造函数初始化列表不允许全部放在一行。
ConstructorInitializerIndentWidth: 0: 构造函数初始化列表不额外缩进。
ContinuationIndentWidth: 8: 续行缩进宽度为 8 个空格。
DerivePointerBinding: false: 不推导指针绑定。
FixNamespaceComments: false: 不修复命名空间注释。
IncludeBlocks: Preserve: 保留 include 块的顺序。
IndentCaseLabels: false: case 标签不缩进。
IndentPPDirectives: AfterHash: 预处理器指令的缩进在 # 后。
IndentWidth: 8: 缩进宽度为 8 个空格。
KeepEmptyLinesAtTheStartOfBlocks: false: 不保留块开头的空行。
MaxEmptyLinesToKeep: 1: 最多保留 1 行空行。
NamespaceIndentation: None: 命名空间不缩进。
PenaltyBreakBeforeFirstCallParameter: 19: 在函数调用的第一个参数前换行的惩罚分数。
PenaltyBreakComment: 300: 注释前换行的惩罚分数。
PenaltyBreakString: 1000: 字符串字面量前换行的惩罚分数。
PenaltyExcessCharacter: 1000000: 超出列限制的惩罚分数。
PenaltyReturnTypeOnItsOwnLine: 60: 返回类型单独一行的惩罚分数。
PointerAlignment: Left: 指针对齐方式为左对齐。
ReflowComments: false: 不重排注释。
SortIncludes: false: 不排序 include 语句。
SortUsingDeclarations: false: 不排序 using 声明。
SpaceAfterCStyleCast: false: C 风格的强制类型转换后不留空格。
SpaceAfterTemplateKeyword: false: 模板关键字后不留空格。
SpaceBeforeCpp11BracedList: false: C++11 花括号列表前不留空格。
SpaceBeforeInheritanceColon: false: 继承冒号前不留空格。
SpaceBeforeRangeBasedForLoopColon: false: 范围 for 循环冒号前不留空格。
Standard: Cpp11: 使用 C++11 标准。
UseCRLF: false: 不使用 CRLF 行结束符。



# 多语言混合项目
项目下设置.editorconfig 文件，设置不同语言的代码风格。
```.editorconfig 
# .editorconfig
root = true

[*.py]
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true

[*.c]
indent_style = tab
tab_width = 8
trim_trailing_whitespace = true
insert_final_newline = true

[*.h]
indent_style = tab
tab_width = 8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{mk,make}]
indent_style = tab
tab_width = 8

```


# 配置rust
在根目录下创建.vscode/settings.json 文件，添加以下内容：
```json
      "rust-analyzer.linkedProjects": [
                "sdk/partition/partition/Cargo.toml"
        ]
```