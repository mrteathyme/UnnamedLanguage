# Paradigm
Multi-paradigm

# Syntax rules
- Modified form of pythonic, some "rules" such as functions should start lower case and classes should start Uppercase are not enforced in standard pythonic for example, enforcing those rules should result in more readable code
  
  Infact, the ultimate goal should be that code is readable even without syntax highlighting

- Strong typing, any and all conversions should be intentional,  int(string) is more readable than an implicit conversion of a string to an int as the latter requires the reader to keep track of any type mutations when following flow

- Variable definitions will use the following format, and support both static typing and dynamic typing, static typing will be the preferred method for both speed and memory safety, but allowing for dynamic typing is preferrable for fast prototyping and readability: 
    ```
    Declaration with static type
    name: Type
	Declaration with static type and inline assignment
	name: Type = value
    Declaration with dynamic typing
    name = value
	```
    This can also be interpreted as : being a typing/casting operator (though at this stage in design (30/08/2022) this is not yet decided in design and is merely an inference)

- primitive data types
    Arbitrary Precision Arithmetic: integer/i float/f
    Fixed Precision Arithmetic: integerBits/iBits, floatBits/fBits e.g integer32, i32, float32, f32
    Boolean: True, False, maybe?(Im wary of adding ternary logic on the basis that I would like to avoid "maybe ill need this in the future" design and as of right now i cant think of any practical use cases for ternary logic)
