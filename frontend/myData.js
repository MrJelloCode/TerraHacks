import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';

const MyData = ({ goBack }) => {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    weight: '',
    height: '',
    alcohol: '',
    smoking: ''
  });

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('http://your-backend-api.com/user-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      Alert.alert('Success', 'Data submitted successfully!');
    } catch (err) {
      Alert.alert('Error', 'Failed to submit data.');
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.banner}>
        <TouchableOpacity onPress={goBack}>
          <Text style={styles.backText}>{'<'} Back                 MEDICAL DATA</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.body}>
        {Object.entries({
          age: 'Age',
          gender: 'Gender',
          weight: 'Weight (kg)',
          height: 'Height (cm)',
          alcohol: 'Alcohol Consumption (drinks/week)',
          smoking: 'Smoking Status (Yes/No)'
        }).map(([key, label]) => (
          <View key={key} style={styles.inputGroup}>
            <Text style={styles.label}>{label}</Text>
            <TextInput
              style={styles.input}
              value={formData[key]}
              onChangeText={(value) => handleChange(key, value)}
              placeholder={label}
              placeholderTextColor="#aaa"
            />
          </View>
        ))}

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.submitButtonText}>Submit</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f1fcff'
  },
  scrollContent: {
    paddingBottom: 40
  },
  banner: {
    backgroundColor: '#ade8f4',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    marginTop: 55,
    marginHorizontal: 12
  },
  backText: {
    fontWeight: 'bold',
    fontSize: 16,
    color: '#023047'
  },
  body: {
    padding: 20
  },
  inputGroup: {
    marginBottom: 7
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 15,
    color: '#023047'
  },
  input: {
    height: 44,
    backgroundColor: '#fff',
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    color: '#000'
  },
  submitButton: {
    backgroundColor: '#0077b6',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20
  },
  submitButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16
  }
});

export default MyData;
