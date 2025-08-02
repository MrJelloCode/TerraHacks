// myData.js
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const MyData = ({ goBack }) => {
  return (
    <View style={styles.container}>
      {/* Top Banner */}
      <View style={styles.banner}>
        <TouchableOpacity onPress={goBack}>
          <Text style={styles.backText}>{'<'} Back                 MEDICAL DATA</Text>
        </TouchableOpacity>
      </View>

      {/* Body Content */}
      <View style={styles.body}>
        <Text style={styles.sectionTitle}>Apple Watch & Blood Data Summary</Text>
        <Text style={styles.infoText}>• Heart rate average: 72 bpm</Text>
        <Text style={styles.infoText}>• Step count average: 9,400 steps/day</Text>
        <Text style={styles.infoText}>• SpO₂ average: 97%</Text>
        <Text style={styles.infoText}>• ALT: 58 U/L</Text>
        <Text style={styles.infoText}>• Triglycerides: 134 mg/dL</Text>
        <Text style={styles.infoText}>• ASL: 34 U/L</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f1fcff'
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
    flex: 1,
    padding: 20
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#023047'
  },
  infoText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8
  }
});

export default MyData;
