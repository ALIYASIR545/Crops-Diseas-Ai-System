import { useState } from 'react';
import {
  ActivityIndicator,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL ||
  (Platform.OS === 'android' ? 'http://10.0.2.2:5000' : 'http://127.0.0.1:5000');

type HistoryItem = {
  id: number;
  farmer_id: string;
  crop: string;
  disease_name: string;
  confidence: number;
  weather_risk: string;
  created_at: string;
};

type AlertItem = {
  id: number;
  region: string;
  crop: string;
  disease: string;
  risk_level: string;
  message_en: string;
  message_ur: string;
};

export default function HistoryScreen() {
  // Form and view state for history/alerts screen.
  const [farmerId, setFarmerId] = useState('farmer-001');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadHistory = async () => {
    // Load both cards in parallel: detection history + outbreak alerts.
    setLoading(true);
    setError('');

    try {
      const [historyRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/history?farmer_id=${encodeURIComponent(farmerId)}&limit=20&lang=en`),
        fetch(`${API_BASE_URL}/api/alerts`),
      ]);

      const historyData = await historyRes.json();
      const alertsData = await alertsRes.json();

      if (!historyRes.ok) {
        throw new Error(historyData.error || 'Failed to load history.');
      }
      if (!alertsRes.ok) {
        throw new Error(alertsData.error || 'Failed to load alerts.');
      }

      setHistory(historyData.items ?? []);
      setAlerts(alertsData.items ?? []);
    } catch (err: any) {
      setError(err.message || 'Cannot connect backend.');
    } finally {
      setLoading(false);
    }
  };

  const deleteHistoryRow = async (historyId: number) => {
    // Delete one history item and update local list immediately.
    try {
      setError('');
      const response = await fetch(
        `${API_BASE_URL}/api/history/${historyId}?farmer_id=${encodeURIComponent(farmerId)}`,
        { method: 'DELETE' },
      );
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to delete history item.');
      }
      setHistory((prev) => prev.filter((item) => item.id !== historyId));
    } catch (err: any) {
      setError(err.message || 'Delete failed.');
    }
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>History and Alerts</Text>
      <Text style={styles.subtitle}>Track previous detections and outbreak notifications.</Text>

      <Text style={styles.label}>Farmer ID</Text>
      <TextInput style={styles.input} value={farmerId} onChangeText={setFarmerId} />
      <TouchableOpacity style={styles.primaryBtn} onPress={loadHistory}>
        <Text style={styles.primaryBtnText}>Load Records</Text>
      </TouchableOpacity>

      {loading ? <ActivityIndicator size="large" color="#177245" style={{ marginTop: 12 }} /> : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.card}>
        {/* Card 1: prediction history list */}
        <Text style={styles.cardTitle}>Detection History</Text>
        {history.length === 0 ? (
          <Text style={styles.muted}>No records yet.</Text>
        ) : (
          history.map((item) => (
            <View style={styles.row} key={item.id}>
              <Text style={styles.rowTitle}>{item.disease_name}</Text>
              <Text style={styles.muted}>
                {item.crop || 'Unknown crop'} | {(item.confidence * 100).toFixed(2)}% | risk:
                {' '}
                {item.weather_risk}
              </Text>
              <Text style={styles.muted}>{item.created_at}</Text>
              <TouchableOpacity style={styles.deleteBtn} onPress={() => deleteHistoryRow(item.id)}>
                <Text style={styles.deleteBtnText}>Delete</Text>
              </TouchableOpacity>
            </View>
          ))
        )}
      </View>

      <View style={styles.card}>
        {/* Card 2: active disease alerts */}
        <Text style={styles.cardTitle}>Real-Time Alerts</Text>
        {alerts.length === 0 ? (
          <Text style={styles.muted}>No active alerts.</Text>
        ) : (
          alerts.map((alert) => (
            <View style={styles.row} key={alert.id}>
              <Text style={styles.rowTitle}>
                {alert.region} | {alert.crop} | {alert.disease}
              </Text>
              <Text style={styles.muted}>Risk: {alert.risk_level}</Text>
              <Text style={styles.muted}>{alert.message_en}</Text>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f3f8f2',
  },
  content: {
    padding: 18,
    paddingBottom: 32,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#15341e',
  },
  subtitle: {
    marginTop: 6,
    marginBottom: 12,
    color: '#446052',
  },
  label: {
    marginBottom: 6,
    color: '#204732',
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#d4e6d8',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  primaryBtn: {
    marginTop: 10,
    backgroundColor: '#177245',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  primaryBtnText: {
    color: '#fff',
    fontWeight: '700',
  },
  error: {
    marginTop: 10,
    color: '#af1f1f',
    fontWeight: '600',
  },
  card: {
    marginTop: 14,
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#d4e6d8',
    padding: 12,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#173a23',
    marginBottom: 8,
  },
  row: {
    borderTopWidth: 1,
    borderTopColor: '#eef5ef',
    paddingTop: 8,
    marginTop: 8,
  },
  rowTitle: {
    color: '#1b3a26',
    fontWeight: '700',
  },
  muted: {
    color: '#4f6b5b',
    marginTop: 3,
  },
  deleteBtn: {
    marginTop: 8,
    alignSelf: 'flex-start',
    backgroundColor: '#fbe7e4',
    borderColor: '#efc1b9',
    borderWidth: 1,
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  deleteBtnText: {
    color: '#8c2f1f',
    fontWeight: '700',
  },
});
