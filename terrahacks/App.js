import React, { useState, useEffect } from 'react';
import { Animated } from 'react-native';
import { View, Text, StyleSheet, Modal, TouchableOpacity, TextInput, SafeAreaView } from 'react-native';
import Svg, { Polyline, Line, Text as SvgText } from 'react-native-svg';

const SECTION_SPACING = 14;

const COLORS = {
  bg: '#f8f9fa',
  primary: '#0077b6',
  secondary: '#90e0ef',
  accent: '#ffb703',
  danger: '#ef476f',
  textPrimary: '#023047',
  textSecondary: '#6c757d',
  card: '#ffffff',
  scoreLow: '#06d6a0',
  scoreMid: '#ffd166',
  scoreHigh: '#ef476f'
};

export default function App() {
  const [bgAnim] = useState(new Animated.Value(0));
  const [modalScale] = useState(new Animated.Value(0.8));
  const [modalOpacity] = useState(new Animated.Value(0));

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

  const score = 80;
  const getScoreColor = () => {
    if (score < 30) return COLORS.scoreHigh;
    if (score < 75) return COLORS.scoreMid;
    return COLORS.scoreLow;
  };

  const openModal = (setVisible) => {
    setVisible(true);
    Animated.parallel([
      Animated.timing(modalOpacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true
      }),
      Animated.spring(modalScale, {
        toValue: 1,
        useNativeDriver: true
      })
    ]).start();
  };

  const closeModal = (setVisible) => {
    Animated.parallel([
      Animated.timing(modalOpacity, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true
      }),
      Animated.timing(modalScale, {
        toValue: 0.8,
        duration: 200,
        useNativeDriver: true
      })
    ]).start(() => setVisible(false));
  };

  return (
    <Animated.View style={[styles.safeArea, { backgroundColor: bgInterpolate }]}> 
      <Animated.ScrollView style={[styles.container, { backgroundColor: bgInterpolate }]} contentContainerStyle={styles.scrollContent}>

        <View style={[styles.header, { marginBottom: SECTION_SPACING }]}><Text style={styles.headerText}>Welcome, Malaravan</Text></View>

        <View style={[styles.liverBox, { marginBottom: SECTION_SPACING }]}><Text style={styles.boxLabel}>Liver Model</Text></View>

        <TouchableOpacity style={[styles.combinedRiskBoxFull, { marginBottom: SECTION_SPACING }]} activeOpacity={0.85} onPress={() => openModal(setRiskModalVisible)}>
          <View>
            <Text style={[styles.boxLabel, { color: COLORS.textPrimary }]}>⚠️</Text>
            <View style={styles.bullet}><Text style={styles.bulletText}>• ALT elevated – potential liver strain</Text></View>
            <View style={styles.bullet}><Text style={styles.bulletText}>• Low sleep – less than 5h average</Text></View>
            <View style={styles.bullet}><Text style={styles.bulletText}>• High stress – above normal threshold</Text></View>
          </View>
          <View style={styles.scoreCircleWrapper}>
            <View style={[styles.scoreCircle, { borderColor: getScoreColor(), backgroundColor: '#fff' }]}><Text style={styles.scoreText}>{score}</Text></View>
          </View>
        </TouchableOpacity>

        <Modal visible={riskModalVisible} animationType="none" transparent>
          <View style={styles.modalBackdrop}>
            <Animated.View style={[styles.modalBox, styles.enhancedModalBox, { transform: [{ scale: modalScale }], opacity: modalOpacity }]}>
              <Text style={styles.modalTitle}>Risk Details</Text>
              <Text style={styles.modalText}>- ALT is elevated, indicating potential liver strain.</Text>
              <Text style={styles.modalText}>- Sleep patterns below 5hr average last 3 days.</Text>
              <TouchableOpacity onPress={() => closeModal(setRiskModalVisible)} style={[styles.modalButton, { backgroundColor: COLORS.danger }]}>
                <Text style={[styles.modalButtonText, { color: '#fff' }]}>Close</Text>
              </TouchableOpacity>
            </Animated.View>
          </View>
        </Modal>

        <TouchableOpacity style={[styles.simulateButton, { marginBottom: SECTION_SPACING }]} activeOpacity={0.8} onPress={() => openModal(setSimulateModalVisible)}>
          <Text style={styles.simulateText}>Simulate a Situation</Text>
        </TouchableOpacity>

        <Modal visible={simulateModalVisible} animationType="none" transparent>
          <View style={styles.modalBackdrop}>
            <Animated.View style={[styles.modalBox, { transform: [{ scale: modalScale }], opacity: modalOpacity }]}>
              <Text style={styles.modalTitle}>Simulation</Text>
              <TextInput
                style={styles.simulateInput}
                multiline
                placeholder="e.g. What if I drank 4 beers and only slept 3 hours?"
                value={simulationText}
                onChangeText={setSimulationText}
              />
              <View style={styles.modalButtonRow}>
                <TouchableOpacity onPress={() => closeModal(setSimulateModalVisible)} style={styles.modalButtonAlt} activeOpacity={0.85}>
                  <Text style={styles.modalButtonText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => closeModal(setSimulateModalVisible)} style={styles.modalButton} activeOpacity={0.85}>
                  <Text style={styles.modalButtonText}>Run Simulation</Text>
                </TouchableOpacity>
              </View>
            </Animated.View>
          </View>
        </Modal>

        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.navButton} activeOpacity={0.85}>
            <Text style={styles.navButtonText}>View Reports</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navButton} activeOpacity={0.85}>
            <Text style={styles.navButtonText}>Medical Data</Text>
          </TouchableOpacity>
        </View>

      </Animated.ScrollView>
    </Animated.View>
  );
}

const styles = StyleSheet.create({

  safeArea: { flex: 1 },
  container: { flex: 1 },
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
    backgroundColor: '#e8f4fc',
    padding: 16,
    borderRadius: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.12,
    shadowRadius: 3,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#90e0ef'
  },
  bullet: {
    marginTop: 6,
    paddingLeft: 8,
    borderLeftWidth: 3,
    borderLeftColor: COLORS.primary,
    marginBottom: 4
  },
  bulletText: {
    color: COLORS.textPrimary,
    fontSize: 14
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
    marginTop: 25,

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
  },
  // previous styles...
  modalText: {
    fontSize: 14,
    marginBottom: 6,
    color: '#333'
  },
  enhancedModalBox: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '85%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0'
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    paddingHorizontal: 10
  },
  navButton: {
    backgroundColor: COLORS.secondary,
    padding: 18,
    borderRadius: 12,
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 6
  },
  navButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.textPrimary
  },   liverBox: {
    backgroundColor: COLORS.secondary,
    borderRadius: 12,
    padding: 18,
    marginHorizontal: 2,
    height: 400,
    justifyContent: 'center',
    alignItems: 'center'
  },
  bottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: 16,
    marginTop: 16
  },
  riskBoxContainer: {
    flex: 1,
    marginRight: 12
  },
  riskBox: {
    marginHorizontal: -14,
    backgroundColor: '#e8f4ff',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#c5d9eb',
    height: 140
  },
  scoreWrapper: {
    justifyContent: 'center'
  },
  scoreCircle: {
    width: 80,
    marginLeft: -1,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center'
  },
  scoreText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.textPrimary
  },
  bullet: {
    marginVertical: 2
  },
  bulletText: {
    fontSize: 14,
    color: COLORS.textPrimary
  },

     combinedRiskBoxFull: {
    flexDirection: 'row',
    backgroundColor: '#e8f4fc',
    borderRadius: 12,
    padding: 14,
    marginTop: 20,
    marginHorizontal: 10,
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  scoreCircleWrapper: {
    paddingLeft: 12
  }
});
