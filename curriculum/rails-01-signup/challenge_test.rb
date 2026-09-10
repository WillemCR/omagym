# frozen_string_literal: false
require 'minitest/autorun'
require 'active_model'
require_relative 'app/models/signup_form'
class SignupTest < Minitest::Test
  def form(**changes)
    SignupForm.new(**{name:'Ada',email:'ada@example.test',age:18,terms:true}.merge(changes))
  end
  def test_valid_form_and_model_contract
    f=form; assert f.valid?; assert_empty f.errors; refute f.persisted?; assert_equal('SignupForm',f.model_name.name)
  end
  def test_name_presence
    [nil,'','  '].each { |name| f=form(name:name); refute f.valid?; refute_empty f.errors[:name] }
  end
  def test_email_contract
    [nil,'','a','@b','a@','a@@b','a b@c','a@b c'].each { |email| f=form(email:email); refute f.valid?; refute_empty f.errors[:email] }; assert form(email:'a@b').valid?
  end
  def test_integer_adult_age
    [nil,'no',17,-1,18.5,'18.5'].each { |age| f=form(age:age); refute f.valid?; refute_empty f.errors[:age] }; assert form(age:'18').valid?
  end
  def test_terms_acceptance
    [nil,false,'0','yes',1].each { |terms| f=form(terms:terms); refute f.valid?; refute_empty f.errors[:terms] }; assert form(terms:'1').valid?
  end
  def test_errors_recomputed
    f=form(name:'',email:'bad',age:1,terms:false); refute f.valid?; assert_equal(%i[age email name terms],f.errors.attribute_names.sort); f.name='Ada';f.email='a@b';f.age=20;f.terms=true;assert f.valid?;assert_empty f.errors
  end
end
