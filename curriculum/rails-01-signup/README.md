# Signup form object

Validate a signup form without creating database records.

- Complete SignupForm using ActiveModel::Model and attributes name, email, age, terms. Construct it using keyword/hash attributes and expose standard valid? and errors behavior.
- name must be present (blank whitespace is invalid). email must match the deliberately small rule: exactly one @, non-empty text on each side, and no whitespace anywhere. A dot is not required.
- age must be a numerical integer of at least 18. Numeric strings such as "18" are accepted; nil, non-numeric text and decimals are rejected.
- Only boolean true and string "1" are accepted for terms. nil, false, "0", and other values are invalid.
- Invalid attributes must have entries on their own errors keys. After correcting values, valid? must recompute and clear previous errors. This form is never persisted and uses no database.

Start in `app/models/signup_form.rb`. The gym supplies its project-local Rails, SQLite and Minitest bundle. Tests bootstrap real Rails components with an in-memory database when needed; no separate server is required.

Run `bundle exec ruby challenge_test.rb --verbose` with the gym Gemfile selected via `BUNDLE_GEMFILE`. The gym restores the original grading suite for each run.

## Documentation

- [Active Model basics](https://guides.rubyonrails.org/active_model_basics.html)
- [Rails validations](https://guides.rubyonrails.org/active_record_validations.html)
