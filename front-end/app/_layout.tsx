import {Stack} from 'expo-router';
import {Provider} from "react-redux";
import {store} from "./redux/store";
import {rehydrateStopsFavorites} from "@/app/redux/favStopsSlice";
import {rehydrateRoutesFavorites} from "@/app/redux/favRoutesSlice";
import {useEffect} from "react";
import { LogBox } from 'react-native';

LogBox.ignoreLogs([
    'Warning: Each child in a list should have a unique "key" prop.',
    'Warning: Encountered two children with the same key',
]);

export default function Layout() {
    useEffect(() => {
        const loadFavorites = async () => {
            await Promise.all([
                rehydrateRoutesFavorites(store.dispatch), // Rehydrate the favorites
                rehydrateStopsFavorites(store.dispatch)
            ]);
        };

    //  Return the promise from `loadFavorites` to handle it explicitly
        loadFavorites().catch(error => console.error('Favourite rehydration error:', error));
    }, []);


    return (
      <Provider store={store}>
          <Stack
              screenOptions={{headerShown: false}}>
              <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          </Stack>
      </Provider>
  );
}
