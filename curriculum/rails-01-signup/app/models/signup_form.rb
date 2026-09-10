require 'active_model'
class SignupForm
  include ActiveModel::Model
  attr_accessor :name, :email, :age, :terms
  # Add the form validation contract here.
end
