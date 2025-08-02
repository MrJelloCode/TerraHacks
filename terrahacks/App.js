import React, { useState, useEffect } from 'react';
import { Animated } from 'react-native';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TextInput, SafeAreaView } from 'react-native';

const COLORS = {
  bg: '#f8f9fa',
  primary: '#0077b6',
  secondary: '#90e0ef',
  accent: '#ffb703',
  danger: '#ef476f',
  textPrimary: '#023047',
  textSecondary: '#6c757d',
  card: '#ffffff',
  scoreLow: '#06d6a0', // Green for good
  scoreMid: '#ffd166', // Yellow for moderate
  scoreHigh: '#ef476f' // Red for poor
};

export default function App() {
  const [bgAnim] = useState(new Animated.Value(0));
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(bgAnim, { toValue: 1, duration: 3000, useNativeDriver: false }),
        Animated.timing(bgAnim, { toValue: 0, duration: 3000, useNativeDriver: false })
      ])
    ).start();
  }, []);

  const bgInterpolate = bgAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['#f8f9fa', '#cde4fa']
  });

  const [riskModalVisible, setRiskModalVisible] = useState(false);
  const [simulateModalVisible, setSimulateModalVisible] = useState(false);
  const [simulationText, setSimulationText] = useState('');

  const score = 20;
  const getScoreColor = () => {
    if (score < 30) return COLORS.scoreHigh;
    if (score < 75) return COLORS.scoreMid;
    return COLORS.scoreLow;
  };

  return (
    <Animated.View style={[styles.safeArea, { backgroundColor: bgInterpolate }]}> 
      <Animated.ScrollView style={[styles.container, { backgroundColor: bgInterpolate }]} contentContainerStyle={styles.scrollContent}>

        {/* Header */}
        <View style={styles.header}><Text style={styles.headerText}>Welcome, Malaravan</Text></View>

        {/* Liver Model & Risks/Score Section */}
        <View style={styles.topSection}>
          <View style={styles.liverBox}><Text style={styles.boxLabel}>Liver Model</Text></View>
          <View style={styles.rightColumn}>
            <TouchableOpacity style={styles.riskBox} activeOpacity={0.85} onPress={() => setRiskModalVisible(true)}>
              <Text style={styles.boxLabel}>Risks / Alerts</Text>
              <View style={styles.bullet}><Text>• ALT elevated</Text></View>
              <View style={styles.bullet}><Text>• Low sleep</Text></View>
            </TouchableOpacity>
            <View style={[styles.scoreCircle, { borderColor: getScoreColor() }]}><Text style={styles.scoreText}>{score}</Text></View>
          </View>
        </View>

        {/* Risk Modal */}
        <Modal visible={riskModalVisible} animationType="slide" transparent>
          <View style={styles.modalBackdrop}>
            <View style={styles.modalBox}>
              <Text style={styles.modalTitle}>Risk Details</Text>
              <Text>- ALT is elevated, indicating potential liver strain.</Text>
              <Text>- Sleep patterns below 5hr average last 3 days.</Text>
              <TouchableOpacity onPress={() => setRiskModalVisible(false)} style={styles.modalButton}>
                <Text style={styles.modalButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        {/* Simulate Button */}
        <TouchableOpacity style={styles.simulateButton} activeOpacity={0.8} onPress={() => setSimulateModalVisible(true)}>
          <Text style={styles.simulateText}>Simulate a Situation</Text>
        </TouchableOpacity>

        {/* Simulate Modal */}
        <Modal visible={simulateModalVisible} animationType="slide" transparent>
          <View style={styles.modalBackdrop}>
            <View style={styles.modalBox}>
              <Text style={styles.modalTitle}>Simulation</Text>
              <TextInput
                style={styles.simulateInput}
                multiline
                placeholder="e.g. What if I drank 4 beers and only slept 3 hours?"
                value={simulationText}
                onChangeText={setSimulationText}
              />
              <View style={styles.modalButtonRow}>
                <TouchableOpacity onPress={() => setSimulateModalVisible(false)} style={styles.modalButtonAlt} activeOpacity={0.85}>
                  <Text style={styles.modalButtonText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => setSimulateModalVisible(false)} style={styles.modalButton} activeOpacity={0.85}>
                  <Text style={styles.modalButtonText}>Run Simulation</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        {/* Charts */}
        <View style={styles.chartRow}>
          <View style={styles.chartBox}><Text style={styles.boxLabel}>Chart: ALT Levels</Text></View>
          <View style={styles.chartBox}><Text style={styles.boxLabel}>Chart: Sleep vs Alcohol</Text></View>
        </View>

      </Animated.ScrollView>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1
  },
  container: {
    flex: 1
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 60,
    paddingTop: 55,
    opacity: 1
  },
  header: {
    padding: 10,
    backgroundColor: COLORS.secondary,
    borderRadius: 10,
    marginBottom: 10
  },
  headerText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary
  },
  topSection: {
    flexDirection: 'row',
    marginTop: 10,
    marginBottom: 10
  },
  liverBox: {
    flex: 2,
    backgroundColor: COLORS.secondary,
    padding: 40,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.15,
    shadowRadius: 3,
    elevation: 3
  },
  rightColumn: {
    flex: 1,
    marginLeft: 10,
    justifyContent: 'space-between',
    paddingVertical: 10
  },
  riskBox: {
    backgroundColor: COLORS.primary,
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.15,
    shadowRadius: 3,
    elevation: 3
  },
  bullet: {
    marginTop: 4
  },
  scoreCircle: {
    borderRadius: 60,
    width: 100,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    borderWidth: 6,
    backgroundColor: COLORS.card,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 6
  },
  scoreText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary
  },
  simulateButton: {
    marginTop: 20,
    backgroundColor: COLORS.primary,
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4
  },
  simulateText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white'
  },
  chartRow: {
    flexDirection: 'column',
    marginTop: 20,
    gap: 16
  },
  chartBox: {
    width: '100%',
    backgroundColor: COLORS.card,
    padding: 28,
    borderRadius: 16,
    marginBottom: 16,
    minHeight: 150,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 5,
    elevation: 5
  },
  boxLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333'
  },
  modalBackdrop: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)'
  },
  modalBox: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    width: '85%'
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10
  },
  modalButtonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  modalButton: {
    marginTop: 15,
    backgroundColor: '#a5d6a7',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    flex: 1,
    marginLeft: 5
  },
  modalButtonAlt: {
    marginTop: 15,
    backgroundColor: '#f8bbbb',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    flex: 1,
    marginRight: 5
  },
  modalButtonText: {
    color: '#124f1f',
    fontWeight: 'bold'
  },
  simulateInput: {
    height: 100,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    marginTop: 10,
    textAlignVertical: 'top'
  }
});
