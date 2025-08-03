import React, { useState, useEffect, CSSProperties } from 'react';
import { Animated, View, Text, StyleSheet, Modal, TouchableOpacity, TextInput, ScrollView, Image } from 'react-native';
import Reports from './reports';
import MyData from './myData';
import { RotateCcw, SkipBack, Rewind, FastForward, SkipForward } from 'lucide-react-native';

import { BallLoader } from "react-spinners";


const SECTION_SPACING = 5;

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


const override = {
  display: "block",
  margin: "0 auto",
  borderColor: "red",
};

export function LoadingBar({ loading }) {
  return (
    <div>
      <p>Fetching information from server...</p>
      <BallLoader
        color={COLORS.primary}
        loading={loading}
        cssOverride={override}
        size={150}
        aria-label="Loading Spinner"
        data-testid="loader"
      />
    </div>
  );
}

export default function App() {
  const [bgAnim] = useState(new Animated.Value(0));
  const [modalScale] = useState(new Animated.Value(0.8));
  const [modalOpacity] = useState(new Animated.Value(0));
  const [currentDate, setCurrentDate] = useState(new Date('2025-08-03'));
  const [loading, setLoading] = useState(true);
  const [prompt, setPrompt] = useState("");
  const [dayData, setDayData] = useState(null);


  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(bgAnim, { toValue: 1, duration: 3000, useNativeDriver: false }),
        Animated.timing(bgAnim, { toValue: 0, duration: 3000, useNativeDriver: false })
      ])
    ).start();
  }, [currentDate]);

  const [idleAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(idleAnim, {
          toValue: -10,
          duration: 1500,
          useNativeDriver: true
        }),
        Animated.timing(idleAnim, {
          toValue: 0,
          duration: 1500,
          useNativeDriver: true
        })
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
  const [showReports, setShowReports] = useState(false);
  const [showmyData, setShowmyData] = useState(false);

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

  const formatDate = (date) => date.toISOString().split('T')[0];

  const changeDate = (days) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setDate(newDate.getDate() + days);
      return newDate;
    });
  };

  if (showReports) return <Reports goBack={() => setShowReports(false)} bgInterpolate={bgInterpolate} />;
  if (showmyData) return <MyData goBack={() => setShowmyData(false)} bgInterpolate={bgInterpolate} />;

  const url = "http://ec2-18-118-9-175.us-east-2.compute.amazonaws.com"

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${url}/get_or_simulate_day`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            timestamp: currentDate.toISOString(),
            prompt: prompt,
          }),
        });
        const data = await response.json();
        setDayData(data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [currentDate, prompt]);

  return (
    <div>
      <Animated.View style={[styles.safeArea, { backgroundColor: bgInterpolate }]}>
        <Animated.ScrollView style={[styles.container, { backgroundColor: bgInterpolate }]} contentContainerStyle={styles.scrollContent}>

          <View style={[styles.header, { marginBottom: SECTION_SPACING }]}><Text style={styles.headerText}>Welcome, Malaravan</Text></View>

          <View style={[styles.liverBox, { marginBottom: SECTION_SPACING }]}>
            <Text style={[styles.boxLabel2, { marginBottom: 10 }]}>{formatDate(currentDate)}</Text>

            {loading ? <LoadingBar loading={loading} /> :
              <Animated.Image
                source={url + dayData.liver_sprite}
                style={{
                  width: 64 * 3,
                  height: 64 * 3,
                  marginBottom: 12,
                  transform: [{ translateY: idleAnim }]
                }}
              />
            }

            <View style={{ alignItems: 'center' }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', width: '80%', marginTop: 20 }}>
                <TouchableOpacity onPress={() => changeDate(-7)}><Text style={{ fontSize: 28 }}><SkipBack /></Text></TouchableOpacity>
                <TouchableOpacity onPress={() => changeDate(-1)}><Text style={{ fontSize: 28 }}><Rewind /></Text></TouchableOpacity>
                <TouchableOpacity onPress={() => setCurrentDate(new Date('2025-08-02'))}><Text style={{ fontSize: 28 }}><RotateCcw /></Text></TouchableOpacity>
                <TouchableOpacity onPress={() => changeDate(1)}><Text style={{ fontSize: 28 }}><FastForward /></Text></TouchableOpacity>
                <TouchableOpacity onPress={() => changeDate(7)}><Text style={{ fontSize: 28 }}><SkipForward /></Text></TouchableOpacity>
              </View>
            </View>
          </View>

          {loading ? <View style={styles.chartRow}>
            <View style={styles.chartBox}>
              <Text style={styles.boxLabel}>Loading data...</Text>
            </View>
          </View> :
            <View style={styles.watchSummaryContainer}>
              {dayData["blood_values"].map((item, index) => (
                <View key={index} style={styles.watchDataBox}>
                  <Text style={styles.watchDataLabel}>{item.label}</Text>
                  <Text style={styles.watchDataValue}>{item.value}</Text>
                </View>
              ))}
            </View>
          }
          <TouchableOpacity style={[styles.combinedRiskBoxFull, { marginBottom: SECTION_SPACING }]} activeOpacity={0.85} onPress={() => openModal(setRiskModalVisible)}>
            {loading ?
              <View>
                <Text>Loading data...</Text>
              </View>
              :
              <div>
                <View>
                  <Text style={[styles.boxLabel, , { color: COLORS.textPrimary }]}>⚠️ Risk Analysis</Text>
                  <View style={styles.bullet}><Text style={styles.bulletText}>{dayData && dayData["risks"].size > 0 ? dayData["risks"][0] : ""}</Text></View>
                  <View style={styles.bullet}><Text style={styles.bulletText}>{dayData && dayData["risks"].size > 1 ? dayData["risks"][1] : ""}</Text></View>
                  <View style={styles.bullet}><Text style={styles.bulletText}>{dayData && dayData["risks"].size > 2 ? dayData["risks"][2] : ""}</Text></View>
                </View>
                <View style={styles.scoreCircleWrapper}>
                  <View style={[styles.scoreCircle, { borderColor: getScoreColor(), backgroundColor: '#fff' }]}><Text style={styles.scoreText}>{dayData["index_score"]}</Text></View>
                </View>
              </div>
            }
          </TouchableOpacity>

          <Modal visible={riskModalVisible} animationType="none" transparent>
            <View style={styles.modalBackdrop}>
              <Animated.View style={[styles.modalBox, styles.enhancedModalBox, { transform: [{ scale: modalScale }], opacity: modalOpacity }]}>
                <Text style={styles.modalTitle}>Risk Details</Text>
                  <Text style={styles.modalText}>{dayData["risks"].size > 0 ? dayData["risks"][0] : ""}</Text>
                  <Text style={styles.modalText}>{dayData["risks"].size > 1 ? dayData["risks"][1] : ""}</Text>
                  <Text style={styles.modalText}>{dayData["risks"].size > 2 ? dayData["risks"][2] : ""}</Text>
                <TouchableOpacity onPress={() => closeModal(setRiskModalVisible)} style={[styles.modalButton, { backgroundColor: COLORS.danger }]}>
                  <Text style={[styles.modalButtonText, { color: '#fff' }]}>Close</Text>
                </TouchableOpacity>
              </Animated.View>
            </View>
          </Modal>

          <TouchableOpacity style={[styles.simulateButton, { marginBottom: SECTION_SPACING }]} activeOpacity={0.8} onPress={() => openModal(setSimulateModalVisible)}>
            <Text style={styles.simulateText}>{prompt === "" ? "Simulate a Situation" : "Simulating!"}</Text>
          </TouchableOpacity>

          <Modal visible={simulateModalVisible} animationType="none" transparent>
            <View style={styles.modalBackdrop}>
              <Animated.View style={[styles.modalBox, { transform: [{ scale: modalScale }], opacity: modalOpacity }]}>
                <Text style={styles.modalTitle}>Simulation</Text>
                <TextInput style={styles.simulateInput} multiline placeholder="e.g. What if I was 30 years older maintaining the same exercise?" value={simulationText} onChangeText={setSimulationText} />
                <View style={styles.modalButtonRow}>
                  <TouchableOpacity onPress={() => closeModal(setSimulateModalVisible) && setPrompt("")} style={styles.modalButtonAlt} activeOpacity={0.85}>
                    <Text style={styles.modalButtonText}>Cancel</Text>
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => closeModal(setSimulateModalVisible) && setPrompt(simulationText)} style={styles.modalButton} activeOpacity={0.85}>
                    <Text style={styles.modalButtonText}>Run Simulation</Text>
                  </TouchableOpacity>
                </View>
              </Animated.View>
            </View>
          </Modal>

          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.navButton} activeOpacity={0.85} onPress={() => setShowReports(true)}>
              <Text style={styles.navButtonText}>View Reports</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.navButton} activeOpacity={0.85} onPress={() => setShowmyData(true)}>
              <Text style={styles.navButtonText}>Medical Data</Text>
            </TouchableOpacity>
          </View>

        </Animated.ScrollView>
      </Animated.View>
    </div>
  );
}

// ...styles unchanged


const styles = StyleSheet.create({

  safeArea: { flex: 1 },
  container: { flex: 1 },
  scrollContent: {
    padding: 20,
    paddingBottom: 10,
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
    marginLeft: 10,
    padding: 16,
    borderRadius: 14,
    marginBottom: 1,
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
  }, boxLabel2: {
    fontSize: 20,
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
  }, liverBox: {
    backgroundColor: COLORS.secondary,
    borderRadius: 12,
    padding: 18,
    marginHorizontal: 2,
    height: 370,
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
    marginTop: 40,
    marginLeft: -35,
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
    paddingLeft: 0
  },
  watchSummaryContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: '#f1fcff',
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderRadius: 12,
    marginHorizontal: 10,
    marginTop: 5
  },
  watchDataBox: {
    alignItems: 'center',
    paddingHorizontal: 8
  },
  watchDataLabel: {
    fontSize: 12,
    color: '#6c757d'
  },
  watchDataValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#023047'
  }
});
