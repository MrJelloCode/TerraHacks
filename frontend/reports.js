import { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Modal, Animated } from 'react-native';
import Svg, { Line, Polyline, Text as SvgText } from 'react-native-svg';
import axios from 'axios';

const Reports = ({ goBack }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [riskModalVisible, setRiskModalVisible] = useState(false);
  const [altScaleAnim] = useState(new Animated.Value(0));

  const chartHeight = 100;
  const chartWidth = 300;
  const stepX = chartWidth / 6;
  const stepY = chartHeight / 5;
  const days = ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

  const [altData, setAltData] = useState([30, 45, 60, 58, 55, 43, 40]);
  const [bpmData, setBpmData] = useState([70, 72, 68, 75, 71, 69, 70]);
  const [sleepData, setSleepData] = useState([6.5, 7, 5, 4.5, 6, 7.2, 7]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8080/reports');
        setAltData(response.data.altData);
        setBpmData(response.data.bpmData);
        setSleepData(response.data.sleepData);
      } catch (error) {
        console.error('Error fetching report data:', error);
      }
    };
    fetchData();
  }, []);

  const chartConfigs = [
    { title: 'ALT Levels', data: altData, color: '#ff4d6d' },
    { title: 'BPM (Daily Avg)', data: bpmData, color: '#5c7cfa' },
    { title: 'Sleep (Daily Avg)', data: sleepData, color: '#06d6a0' }
  ];

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

  const renderChart = (label, data, color, showModal) => {
    const maxVal = Math.max(...data);
    const yAxisLabels = Array.from({ length: 6 }, (_, i) => Math.round((maxVal / 5) * (5 - i)));
    const polylinePoints = data.map((val, idx) => `${idx * stepX},${chartHeight - (val / maxVal) * chartHeight}`).join(' ');

    return (
      <View style={styles.card} key={label}>
        <Text style={styles.cardTitle}>{label}</Text>
        <View style={{ flexDirection: 'row' }}>
          <Svg height={chartHeight + 20} width={chartWidth + 30}>
            {yAxisLabels.map((val, idx) => (
              <SvgText
                key={idx}
                x={0}
                y={idx * stepY + 10}
                fontSize="10"
                fill="#777"
              >
                {val}
              </SvgText>
            ))}
            <Polyline
              points={polylinePoints.split(' ').map(pt => {
                const [x, y] = pt.split(',');
                return `${parseFloat(x) + 30},${y}`;
              }).join(' ')}
              fill="none"
              stroke={color}
              strokeWidth="2"
            />
            <Line x1="30" y1={chartHeight} x2={chartWidth + 30} y2={chartHeight} stroke="#ccc" strokeWidth="1" />
          </Svg>
        </View>
        <View style={styles.xLabels}>
          {days.map((day, idx) => (
            <Text key={idx} style={styles.dayLabel}>{day}</Text>
          ))}
        </View>
        {label === 'ALT Levels' && (
          <TouchableOpacity onPress={showModal} style={styles.readMoreButton}>
            <Text style={styles.readMoreText}>What is ALT?</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.bannerHeader}>
        <TouchableOpacity onPress={goBack}>
          <Text style={styles.backText}>{'<'} Back                DAILY REPORTS</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Summary (Past 7 Days)</Text>
          <View style={styles.summaryBox}><Text style={styles.summaryBullet}>•</Text><Text style={styles.summaryLine}>ALT levels trended upward early in the week, peaking at 60 on Tuesday.</Text></View>
          <View style={styles.summaryBox}><Text style={styles.summaryBullet}>•</Text><Text style={styles.summaryLine}>Sleep duration dropped under 5h on Monday and Thursday, slightly recovering afterward.</Text></View>
          <View style={styles.summaryBox}><Text style={styles.summaryBullet}>•</Text><Text style={styles.summaryLine}>Alcohol intake was moderate on 3 of the 7 days, with 4 alcohol-free days.</Text></View>
          <View style={styles.summaryBox}><Text style={styles.summaryBullet}>•</Text><Text style={styles.summaryLine}>Stress levels remained mostly stable, with a single mid-week spike observed.</Text></View>
          <View style={styles.summaryBox}><Text style={styles.summaryBullet}>•</Text><Text style={styles.summaryLine}>Overall liver index held above 60, suggesting steady liver performance.</Text></View>
        </View>

        {chartConfigs.map(cfg => renderChart(cfg.title, cfg.data, cfg.color, showAltModal))}
      </ScrollView>

      <Modal visible={modalVisible} transparent={true} onRequestClose={hideAltModal}>
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

      <Modal visible={riskModalVisible} transparent={true} animationType="slide" onRequestClose={() => setRiskModalVisible(false)}>
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
  container: { flex: 1, backgroundColor: '#e0f7fa' },
  bannerHeader: { backgroundColor: '#ade8f4', paddingVertical: 10, paddingHorizontal: 20, borderRadius: 10, marginTop: 55, marginHorizontal: 12 },
  backText: { color: '#023047', fontWeight: 'bold', fontSize: 16 },
  scrollContent: { padding: 16 },
  summaryCard: { backgroundColor: '#fff', padding: 16, marginBottom: 20, borderRadius: 12, elevation: 1 },
  summaryTitle: { fontSize: 15, fontWeight: '700', marginBottom: 6, color: '#1b4965' },
  summaryBox: { flexDirection: 'row', marginBottom: 4, alignItems: 'flex-start' },
  summaryBullet: { fontSize: 16, lineHeight: 20, color: '#1b4965', marginRight: 6 },
  summaryLine: { flex: 1, fontSize: 13, lineHeight: 18, color: '#355070', fontStyle: 'italic' },
  card: { backgroundColor: '#fff', padding: 16, marginBottom: 20, borderRadius: 12, elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.2, shadowRadius: 1.41 },
  cardTitle: { fontSize: 16, fontWeight: '600', marginBottom: 10 },
  xLabels: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 6, paddingHorizontal: 4 },
  dayLabel: { fontSize: 10, color: '#555', width: 40, textAlign: 'center' },
  readMoreButton: { marginTop: 8, alignSelf: 'flex-start', backgroundColor: '#f0f0f0', paddingVertical: 4, paddingHorizontal: 10, borderRadius: 6 },
  readMoreText: { fontSize: 12, color: '#0077b6' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', alignItems: 'center' },
  modalContent: { backgroundColor: 'white', padding: 20, margin: 20, borderRadius: 12, width: '85%', elevation: 3 },
  modalTitle: { fontSize: 16, fontWeight: '700', marginBottom: 10, color: '#1b4965' },
  modalText: { fontSize: 14, color: '#444', marginBottom: 16 },
  closeButton: { alignSelf: 'flex-end', backgroundColor: '#ff4d6d', paddingVertical: 6, paddingHorizontal: 14, borderRadius: 6 },
  closeText: { color: 'white', fontWeight: '600', fontSize: 13 }
});

export default Reports;
