import React from 'react';
import {View} from 'react-native';
import {shallowEqual, useSelector} from "react-redux";
import {RootState} from "@/app/redux/store";
import {Route} from "@/types/route";
import SearchButtonRoute from "@/components/SearchButtonRoute";

export const ButtonRoute = () => {


    const routes = useSelector((state: RootState) => state.route.routes, shallowEqual);
    const favs = useSelector((state: RootState) => state.favRoute.routes ?? [], shallowEqual);
    const favRoutes = routes.filter((route: Route) => favs?.includes?.(route.name));

    return (
        <View>
            {/* create component for each bus route */}
            {favRoutes.map((route: Route) => (
                <SearchButtonRoute item={route}/>
            ))}
        </View>
    );
};