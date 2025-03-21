import React, { useMemo } from "react";
import { Marker } from "react-native-maps";
    import { Image, View, StyleSheet } from "react-native";
import { router } from "expo-router";

interface StopProps {
    id: string;
    lat: number;
    lon: number;
    name: string;
    code: string;
    direction: number;
}

const StopMarker: React.FC<StopProps> = ({ id, lat, lon, name, code, direction }) => {
    // Cache bus stop icon
    const customBusStop = useMemo(
        () => Image.resolveAssetSource(require('@/assets/images/BusStop.png')).uri,
        []
    );

    return (
        <Marker
            key={id}
            coordinate={{ latitude: lat, longitude: lon }}
            title={name}
            description="Bus Stop"
            // onPress={() => router.push({ pathname: `/screens/arrivals/${id}`, params: { stop: id } })}
            onPress={() => router.push(`/screens/arrivals/${id}`)}
        >
            <View style={{ transform: [{ rotate: `${direction}deg` }] }}>
                <Image source={{ uri: customBusStop }} style={styles.stopIcon} />
            </View>
        </Marker>
    );
};


// Optimize re-renders
export default React.memo(StopMarker);

const styles = StyleSheet.create({
    stopIcon: {
        width: 15,
        height: 15,
        resizeMode: "contain",
    },
});
