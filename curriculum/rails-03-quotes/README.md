# Shipping quote API

Expose a predictable JSON shipping endpoint with Rails request handling.

- Complete ShippingQuotesController < ActionController::API with a create action. Tests dispatch real JSON HTTP POST requests to the action through Rack.
- Request body must have a quote object containing weight_grams and zone. Permit only these two input fields; ignore extra keys. weight_grams must be an Integer from 1 through 20000. zone must be exactly "local" or "international".
- For valid input return status 200 and JSON with exactly cents and currency. currency is "EUR". cents is 300 for local or 900 for international, plus 100 for each started 1000 grams.
- Missing or non-object quote returns status 400 with exactly {"error":"quote_required"}. An object with invalid fields returns status 422 with exactly {"error":"invalid_quote"}.
- Use Rails parameter and JSON rendering facilities. Do not start a listener, make external requests, or persist quotes. Return JSON content type for success and errors.

Start in `app/controllers/shipping_quotes_controller.rb`. The gym supplies its project-local Rails, SQLite and Minitest bundle. Tests bootstrap real Rails components with an in-memory database when needed; no separate server is required.

Run `bundle exec ruby challenge_test.rb --verbose` with the gym Gemfile selected via `BUNDLE_GEMFILE`. The gym restores the original grading suite for each run.

## Documentation

- [Action Controller overview](https://guides.rubyonrails.org/action_controller_overview.html)
- [Rails API applications](https://guides.rubyonrails.org/api_app.html)
