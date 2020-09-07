/*
 * This file is part of GumTree.
 *
 * GumTree is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * GumTree is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with GumTree.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright 2011-2015 Jean-Rémy Falleri <jr.falleri@gmail.com>
 * Copyright 2011-2015 Floréal Morandat <florealm@gmail.com>
 */

package com.github.gumtreediff.client.diff.swing;

import com.github.gumtreediff.gen.Generators;
import com.github.gumtreediff.tree.TreeContext;

import javax.swing.*;
import java.io.IOException;

public final class SwingTree {

    public static void main(String[] args) throws IOException {
        final TreeContext t = Generators.getInstance().getTree(args[0]);
        javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                createAndShow(t);
            }
        });
    }

    private SwingTree() {
    }

    private static void createAndShow(TreeContext tree) {
        JFrame frame = new JFrame("Tree Viewer");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new TreePanel(tree));
        frame.pack();
        frame.setVisible(true);
    }
}