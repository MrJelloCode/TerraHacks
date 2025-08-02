import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Modal, Animated } from 'react-native';
import Svg, { Line, Polyline } from 'react-native-svg';

const Reports = ({ goBack }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [riskModalVisible, setRiskModalVisible] = useState(false);
  const [altScaleAnim] = useState(new Animated.Value(0));

  const altData = [30, 45, 60, 58, 55, 43, 40];
  const maxAlt = Math.max(...altData);
  const chartHeight = 100;
  const chartWidth = 300;
  const stepX = chartWidth / (altData.length - 1);
  const polylinePoints = altData.map((val, idx) => `${idx * stepX},${chartHeight - (val / maxAlt) * chartHeight}`).join(' ');
  const days = ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

  const showAltModal = () => {
    setModalVisible(true);
    Animated.spring(altScaleAnim, {
      toValue: 1,
      friction: 5,
      useNativeDriver: true
    }).start();
  };

  const hideAltModal = () => {
    Animated.timing(altScaleAnim, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true
    }).start(() => setModalVisible(false));
  };

  return (
    <View style={styles.container}>
      {/* Banner Header */}
      <View style={styles.bannerHeader}>
        <TouchableOpacity onPress={goBack}>
          <Text style={styles.backText}>{'<'} Back                DAILY REPORTS</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Summary Card */}
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Summary (Past 7 Days)</Text>
          <View style={styles.summaryBox}>
            <Text style={styles.summaryBullet}>•</Text>
            <Text style={styles.summaryLine}>ALT levels trended upward early in the week, peaking at 60 on Tuesday.</Text>
          </View>
          <View style={styles.summaryBox}>
            <Text style={styles.summaryBullet}>•</Text>
            <Text style={styles.summaryLine}>Sleep duration dropped under 5h on Monday and Thursday, slightly recovering afterward.</Text>
          </View>
          <View style={styles.summaryBox}>
            <Text style={styles.summaryBullet}>•</Text>
            <Text style={styles.summaryLine}>Alcohol intake was moderate on 3 of the 7 days, with 4 alcohol-free days.</Text>
          </View>
          <View style={styles.summaryBox}>
            <Text style={styles.summaryBullet}>•</Text>
            <Text style={styles.summaryLine}>Stress levels remained mostly stable, with a single mid-week spike observed.</Text>
          </View>
          <View style={styles.summaryBox}>
            <Text style={styles.summaryBullet}>•</Text>
            <Text style={styles.summaryLine}>Overall liver index held above 60, suggesting steady liver performance.</Text>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>ALT Levels</Text>
          <Svg height={chartHeight + 20} width={chartWidth}>
            <Polyline
              points={polylinePoints}
              fill="none"
              stroke="#ff4d6d"
              strokeWidth="2"
            />
            <Line x1="0" y1={chartHeight} x2={chartWidth} y2={chartHeight} stroke="#ccc" strokeWidth="1" />
          </Svg>
          <View style={styles.xLabels}>
            {days.map((day, idx) => (
              <Text key={idx} style={styles.dayLabel}>{day}</Text>
            ))}
          </View>
          <TouchableOpacity onPress={showAltModal} style={styles.readMoreButton}>
            <Text style={styles.readMoreText}>What is ALT?</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Chart: Sleep vs Alcohol</Text>
        </View>
      </ScrollView>

      {/* ALT Modal with pop animation */}
      <Modal
        visible={modalVisible}
        transparent={true}
        onRequestClose={hideAltModal}
      >
        <View style={styles.modalOverlay}>
          <Animated.View style={[styles.modalContent, { transform: [{ scale: altScaleAnim }] }]}>
            <Text style={styles.modalTitle}>What is ALT?</Text>
            <Text style={styles.modalText}>
              ALT (Alanine Aminotransferase) is an enzyme found mostly in the liver. It plays a role in breaking down proteins and is released into the blood when the liver is damaged. Monitoring ALT levels helps assess liver health and detect potential liver conditions.
            </Text>
            <TouchableOpacity onPress={hideAltModal} style={styles.closeButton}>
              <Text style={styles.closeText}>Close</Text>
            </TouchableOpacity>
          </Animated.View>
        </View>
      </Modal>

      {/* Risk Analytics Modal */}
      <Modal
        visible={riskModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setRiskModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Risk Analysis Details</Text>
            <Text style={styles.modalText}>
              ALT is elevated — indicating potential liver strain.
              {'\n'}Sleep is consistently low — less than 5hr average.
              {'\n'}Stress levels have exceeded normal range.
            </Text>
            <TouchableOpacity onPress={() => setRiskModalVisible(false)} style={styles.closeButton}>
              <Text style={styles.closeText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#e0f7fa'
  },
  bannerHeader: {
    backgroundColor: '#ade8f4',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    marginTop: 55,
    marginHorizontal: 12
  },
  backText: {
    color: '#023047',
    fontWeight: 'bold',
    fontSize: 16
  },
  scrollContent: {
    padding: 16
  },
  summaryCard: {
    backgroundColor: '#dff6f0',
    padding: 16,
    marginBottom: 20,
    borderRadius: 12,
    elevation: 1
  },
  summaryTitle: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 6,
    color: '#1b4965'
  },
  summaryBox: {
    flexDirection: 'row',
    marginBottom: 4,
    alignItems: 'flex-start'
  },
  summaryBullet: {
    fontSize: 16,
    lineHeight: 20,
    color: '#1b4965',
    marginRight: 6
  },
  summaryLine: {
    flex: 1,
    fontSize: 13,
    lineHeight: 18,
    color: '#355070',
    fontStyle: 'italic'
  },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10
  },
  xLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 6,
    paddingHorizontal: 4
  },
  dayLabel: {
    fontSize: 10,
    color: '#555',
    width: 40,
    textAlign: 'center'
  },
  readMoreButton: {
    marginTop: 8,
    alignSelf: 'flex-start',
    backgroundColor: '#f0f0f0',
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 6
  },
  readMoreText: {
    fontSize: 12,
    color: '#0077b6'
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 12,
    width: '85%',
    elevation: 3
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 10,
    color: '#1b4965'
  },
  modalText: {
    fontSize: 14,
    color: '#444',
    marginBottom: 16
  },
  closeButton: {
    alignSelf: 'flex-end',
    backgroundColor: '#ff4d6d',
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 6
  },
  closeText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 13
  }
});

export default Reports;
